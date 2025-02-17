package com.siemens.licenselynx;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.junit.jupiter.api.Assertions;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.Map;


/**
 * Test class for LicenseLynx.
 */
@ExtendWith(MockitoExtension.class)
class LicenseLynxTest
{

    /**
     * Tests mapping of a non-existing license name.
     */
    @Test
    void testMapNonExistingLicense()
    {
        Map<String, LicenseObject> testMap = new HashMap<>();
        testMap.put("test", new LicenseObject("TestCanonical", "TestSrc"));
        LicenseMapSingleton testInstance = new LicenseMapSingleton(testMap);

        // Arrange
        String licenseName = "nonExistingLicense";

        // Act
        LicenseObject result = LicenseLynx.map(licenseName);

        // Assert
        Assertions.assertNull(result);
    }



    @Test
    void testWithInjectedLicenseMap()
    {
        Map<String, LicenseObject> testMap = new HashMap<>();
        testMap.put("test", new LicenseObject("TestCanonical", "TestSrc"));
        LicenseMapSingleton testInstance = new LicenseMapSingleton(testMap);

        Assertions.assertEquals("TestCanonical", testInstance.getLicenseMap().get("test").getCanonical());
        Assertions.assertEquals("TestSrc", testInstance.getLicenseMap().get("test").getSrc());
    }



    @Test
    void testWithNullValuesInLicenseMap()
    {
        Map<String, LicenseObject> testMap = new HashMap<>();
        testMap.put("test", new LicenseObject(null, null));
        LicenseMapSingleton testInstance = new LicenseMapSingleton(testMap);

        Assertions.assertNull(testInstance.getLicenseMap().get("test").getCanonical());
    }



    @Test
    void testSingletonInstanceAlreadyExists()
        throws Exception
    {
        // First instance creation (valid)
        LicenseMapSingleton firstInstance = LicenseMapSingleton.getInstance();
        Assertions.assertNotNull(firstInstance);

        // Attempt to create another instance using reflection
        Constructor<LicenseMapSingleton> constructor = LicenseMapSingleton.class.getDeclaredConstructor();
        constructor.setAccessible(true); // Bypass private access

        // Attempt instantiation and assert the cause of InvocationTargetException
        InvocationTargetException exception = Assertions.assertThrows(InvocationTargetException.class,
            constructor::newInstance);
        Assertions.assertInstanceOf(InstantiationError.class, exception.getCause());
        Assertions.assertEquals("Instance already exists!", exception.getCause().getMessage());
    }



    @Test
    void testValidSingletonInstance()
    {
        // Ensure getInstance() returns the same object
        LicenseMapSingleton instance1 = LicenseMapSingleton.getInstance();
        LicenseMapSingleton instance2 = LicenseMapSingleton.getInstance();

        Assertions.assertSame(instance1, instance2, "getInstance() should always return the same instance");
    }


}
