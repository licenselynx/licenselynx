/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import org.mockito.junit.jupiter.MockitoExtension;
import org.junit.jupiter.api.Assertions;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;


/**
 * Test class for LicenseLynx.
 */
@ExtendWith(MockitoExtension.class)
class LicenseLynxTest
{
    private final String CANONICAL_ID_SPDX = "testCanonicalSpdx";
    private final String CANONICAL_ID_SCANCODE = "testCanonicalScanCode";
    private final String CANONICAL_ID_SIEMENS = "testCanonicalSiemens";

    /**
     * Tests mapping of a non-existing license name.
     */
    @Test
    void testMapNonExistingLicense()
    {
        // Arrange
        String licenseName = "nonExistingLicense";

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName);
        LicenseObject result2 = LicenseLynx.map(licenseName, true);
        LicenseObject result3 = LicenseLynx.map(licenseName, false);

        // Assert
        Assertions.assertNull(result1);
        Assertions.assertNull(result2);
        Assertions.assertNull(result3);

    }

    @Test
    @SuppressWarnings("deprecation")
    void testMapCanonicalLicense()
    {
        // Arrange
        String licenseNameSpdx = "test-license";
        String licenseNameScancode = "test-risky-license";

        // Act
        LicenseObject result_spdx = LicenseLynx.map(licenseNameSpdx);
        LicenseObject result_scancode = LicenseLynx.map(licenseNameScancode, true);

        // Assert
        assert result_spdx != null;
        assert result_scancode != null;
        Assertions.assertEquals(CANONICAL_ID_SPDX, result_spdx.getId());
        Assertions.assertEquals(CANONICAL_ID_SCANCODE, result_scancode.getId());

        Assertions.assertEquals(LicenseSource.Spdx, result_spdx.getCanonicalSource());
        Assertions.assertEquals(LicenseSource.ScancodeLicensedb, result_scancode.getCanonicalSource());

        Assertions.assertTrue(result_spdx.isSpdxIdentifier());
        Assertions.assertFalse(result_spdx.isScanCodeLicenseDbIdentifier());

        Assertions.assertTrue(result_scancode.isScanCodeLicenseDbIdentifier());
        Assertions.assertFalse(result_scancode.isSpdxIdentifier());

        Assertions.assertEquals(LicenseSource.Spdx.getValue(), result_spdx.getSrc());

    }

    @Test
    void testMapQuotesLicense()
    {
        // Arrange
        String licenseName = "‚test-license‛";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName);

        // Assert
        assert result != null;
        Assertions.assertEquals(CANONICAL_ID_SPDX, result.getId());
        Assertions.assertEquals(LicenseSource.Spdx, result.getCanonicalSource());
    }


    @Test
    void testMapRiskyLicense()
    {
        // Arrange
        String licenseName = "test-risky-license";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, true);

        // Assert
        assert result != null;
        Assertions.assertEquals(CANONICAL_ID_SCANCODE, result.getId());
        Assertions.assertEquals(LicenseSource.ScancodeLicensedb, result.getCanonicalSource());
    }


    @Test
    void testMapRiskyLicenseNotEnabled()
    {
        // Arrange
        String licenseName = "test-risky-license";

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName, false);
        LicenseObject result2 = LicenseLynx.map(licenseName);

        // Assert
        assert result1 == null;
        assert result2 == null;
    }



    @Test
    @SuppressWarnings("deprecation")
    void testWithInjectedLicenseMap()
    {
        // Arrange
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();

        testMap.put("test", new LicenseObject(CANONICAL_ID_SPDX, "spdx"));
        String testCanonicalRisky = "TestCanonicalRisky";
        testRiskyMap.put("testRisky", new LicenseObject(testCanonicalRisky, LicenseSource.Custom));

        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap);
        LicenseMapSingleton testInstance = new LicenseMapSingleton(licenseMap);

        // Act && Assert
        Assertions.assertEquals(CANONICAL_ID_SPDX,
            testInstance.getLicenseMap().getCanonicalLicenseMap().get("test").getId());
        Assertions.assertEquals(LicenseSource.Spdx,
                testInstance.getLicenseMap().getCanonicalLicenseMap().get("test").getCanonicalSource());

        Assertions.assertEquals(LicenseSource.Custom,
                testInstance.getLicenseMap().getRiskyLicenseMap().get("testRisky").getCanonicalSource());
        Assertions.assertTrue(testInstance.getLicenseMap().getRiskyLicenseMap().get("testRisky").isCustomSource());
    }



    @Test
    void testValidSingletonInstance()
    {
        // Arrange && Act
        LicenseMapSingleton instance1 = LicenseMapSingleton.getInstance();
        LicenseMapSingleton instance2 = LicenseMapSingleton.getInstance();

        // Assert
        Assertions.assertSame(instance1, instance2, "getInstance() should always return the same instance");
    }



    @Test
    void testNullInputStream()
    {
        // Arrange
        ClassLoader mockClassLoader = new ClassLoader()
        {
            @Override
            public InputStream getResourceAsStream(final String pName)
            {
                return null;
            }
        };

        LicenseDataLoader loader = new LicenseDataLoader(new ObjectMapper(), mockClassLoader);

        // Act && Assert
        Assertions.assertThrows(IllegalArgumentException.class, loader::loadLicenses);
    }



    @Test
    void testIOException()
    {
        // Arrange
        ClassLoader mockClassLoader = new ClassLoader()
        {
            @Override
            public InputStream getResourceAsStream(final String pName)
            {
                return new InputStream()
                {
                    @Override
                    public int read()
                        throws IOException
                    {
                        throw new IOException("Test IOException");
                    }
                };
            }
        };

        LicenseDataLoader loader = new LicenseDataLoader(new ObjectMapper(), mockClassLoader);

        // Act && Assert
        Assertions.assertThrows(UncheckedIOException.class, loader::loadLicenses);
    }

    @Test
    void testIllegalArgument()
    {
        // Act && Assert
        Assertions.assertThrows(IllegalArgumentException.class, () -> LicenseSource.fromValue("non-specified-source"));
    }

    @Test
    void testOrganizationSource()
    {
        // Arrange
        LicenseObject orgLicense = new LicenseObject("SISL-1.5", Organization.Siemens);

        // Act && Assert
        Assertions.assertEquals("SISL-1.5", orgLicense.getId());
        Assertions.assertEquals(Organization.Siemens, orgLicense.getCanonicalSource());
        Assertions.assertTrue(orgLicense.isOrganizationSource());
        Assertions.assertTrue(orgLicense.isOrganizationSource(Organization.Siemens));
        Assertions.assertFalse(orgLicense.isSpdxIdentifier());
        Assertions.assertFalse(orgLicense.isScanCodeLicenseDbIdentifier());
        Assertions.assertFalse(orgLicense.isCustomSource());
    }

    @Test
    @SuppressWarnings("deprecation")
    void testOrganizationSourceFromString()
    {
        // Arrange && Act
        LicenseObject orgLicense = new LicenseObject("SISL-1.5", "siemens");

        // Assert
        Assertions.assertEquals("SISL-1.5", orgLicense.getId());
        Assertions.assertEquals(Organization.Siemens, orgLicense.getCanonicalSource());
        Assertions.assertTrue(orgLicense.isOrganizationSource());
        Assertions.assertEquals("siemens", orgLicense.getSrc());
    }

    @Test
    @SuppressWarnings("deprecation")
    void testDeprecatedGetLicenseSourceWithLicenseSource()
    {
        // Arrange
        LicenseObject spdxLicense = new LicenseObject("MIT", LicenseSource.Spdx);

        // Act & Assert
        Assertions.assertEquals(LicenseSource.Spdx, spdxLicense.getLicenseSource());
    }

    @Test
    @SuppressWarnings("deprecation")
    void testDeprecatedGetLicenseSourceWithOrganization()
    {
        // Arrange
        LicenseObject orgLicense = new LicenseObject("SISL-1.5", Organization.Siemens);

        // Act && Assert
        Assertions.assertThrows(ClassCastException.class, orgLicense::getLicenseSource);
    }

    @Test
    @SuppressWarnings("deprecation")
    void testNotOrganizationSource()
    {
        // Arrange
        LicenseObject spdxLicense = new LicenseObject("MIT", LicenseSource.Spdx);

        // Assert
        Assertions.assertFalse(spdxLicense.isOrganizationSource());
        Assertions.assertFalse(spdxLicense.isOrganizationSource(Organization.Siemens));
    }

    @Test
    void testUnknownCanonicalSource()
    {
        // Act && Assert
        Assertions.assertThrows(IllegalArgumentException.class,
            () -> CanonicalSourceDeserializer.fromValue("unknown-source"));
    }

    @Test
    void testOrganizationFromValue()
    {
        // Act & Assert
        Assertions.assertEquals(Organization.Siemens, Organization.fromValue("siemens"));
        Assertions.assertThrows(IllegalArgumentException.class, () -> Organization.fromValue("unknown-org"));
    }

    @Test
    @SuppressWarnings("deprecation")
    void testWithInjectedLicenseMapWithOrgs()
    {
        // Arrange
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();
        Map<Organization, Map<String, LicenseObject>> testOrgMaps = new EnumMap<>(Organization.class);

        testMap.put("test", new LicenseObject(CANONICAL_ID_SPDX, LicenseSource.Spdx));

        Map<String, LicenseObject> siemensMap = new HashMap<>();
        siemensMap.put("test-org-license", new LicenseObject("SISL-1.5", Organization.Siemens));
        testOrgMaps.put(Organization.Siemens, siemensMap);

        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap, testOrgMaps);

        // Act && Assert
        Assertions.assertEquals("SISL-1.5",
            licenseMap.getOrganizationMap(Organization.Siemens).get("test-org-license").getId());
        Assertions.assertEquals(Organization.Siemens,
            licenseMap.getOrganizationMap(Organization.Siemens).get("test-org-license").getCanonicalSource());
        Assertions.assertTrue(licenseMap.getOrganizationMaps().containsKey(Organization.Siemens));
    }

    @Test
    void testOrganizationMapEmpty()
    {
        // Arrange
        Map<String, LicenseObject> testMap = new HashMap<>();
        Map<String, LicenseObject> testRiskyMap = new HashMap<>();
        LicenseMap licenseMap = new LicenseMap(testMap, testRiskyMap);

        // Act && Assert
        Assertions.assertNotNull(licenseMap.getOrganizationMap(Organization.Siemens));
        Assertions.assertTrue(licenseMap.getOrganizationMap(Organization.Siemens).isEmpty());
    }

    @Test
    void testMapWithOrganization()
    {
        // Arrange
        String licenseName = "test-org-license";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, Organization.Siemens);

        // Assert
        Assertions.assertNotNull(result);
        Assertions.assertEquals(CANONICAL_ID_SIEMENS, result.getId());
        Assertions.assertEquals(Organization.Siemens, result.getCanonicalSource());
        Assertions.assertTrue(result.isOrganizationSource());
        Assertions.assertTrue(result.isOrganizationSource(Organization.Siemens));
    }

    @Test
    void testMapWithOrganizationAndRisky()
    {
        // Arrange
        String licenseName = "test-org-license";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, true, Organization.Siemens);

        // Assert
        Assertions.assertNotNull(result);
        Assertions.assertEquals(CANONICAL_ID_SIEMENS, result.getId());
        Assertions.assertEquals(Organization.Siemens, result.getCanonicalSource());
    }

    @Test
    void testMapOrganizationLicenseNotFoundWithoutOrg()
    {
        // Arrange
        String licenseName = "test-org-license";

        // Act
        LicenseObject result1 = LicenseLynx.map(licenseName);
        LicenseObject result2 = LicenseLynx.map(licenseName, true);

        // Assert
        Assertions.assertNull(result1);
        Assertions.assertNull(result2);
    }

    @Test
    void testMapNonExistingOrgLicense()
    {
        // Arrange
        String licenseName = "nonExistingOrgLicense";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName, Organization.Siemens);

        // Assert
        Assertions.assertNull(result);
    }
}
