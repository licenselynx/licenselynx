/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import net.jcip.annotations.Immutable;

import javax.annotation.Nonnull;
import java.util.Collections;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;


/**
 * LicenseMap represents the JSON structure containing the canonical license map,
 * the risky license map, and organization-specific license maps.
 * It provides getters to access these properties.
 */
@Immutable
@JsonDeserialize(using = LicenseMapDeserializer.class)
class LicenseMap
{
    private final Map<String, LicenseObject> canonicalLicenseMap;

    private final Map<String, LicenseObject> riskyLicenseMap;

    private final Map<Organization, Map<String, LicenseObject>> organizationMaps;



    /**
     * Constructor for LicenseMap with stable and risky maps only.
     * Organization maps will be empty.
     *
     * @param pCanonicalLicenseMap the stable/canonical license map
     * @param pRiskyLicenseMap the risky license map
     */
    LicenseMap(
        @Nonnull final Map<String, LicenseObject> pCanonicalLicenseMap,
        @Nonnull final Map<String, LicenseObject> pRiskyLicenseMap)
    {
        this(pCanonicalLicenseMap, pRiskyLicenseMap, new EnumMap<>(Organization.class));
    }



    /**
     * Constructor for LicenseMap with stable, risky, and organization maps.
     *
     * @param pCanonicalLicenseMap the stable/canonical license map
     * @param pRiskyLicenseMap the risky license map
     * @param pOrganizationMaps the organization-specific license maps
     */
    LicenseMap(
        @Nonnull final Map<String, LicenseObject> pCanonicalLicenseMap,
        @Nonnull final Map<String, LicenseObject> pRiskyLicenseMap,
        @Nonnull final Map<Organization, Map<String, LicenseObject>> pOrganizationMaps)
    {
        this.canonicalLicenseMap = Objects.requireNonNull(pCanonicalLicenseMap);
        this.riskyLicenseMap = Objects.requireNonNull(pRiskyLicenseMap);
        this.organizationMaps = Objects.requireNonNull(pOrganizationMaps);
    }



    /**
     * Gets the canonical license map.
     * @return canonical license map
     */
    @Nonnull
    Map<String, LicenseObject> getCanonicalLicenseMap()
    {
        return canonicalLicenseMap;
    }



    /**
     * Gets the risky license map.
     * @return risky license map
     */
    @Nonnull
    Map<String, LicenseObject> getRiskyLicenseMap()
    {
        return riskyLicenseMap;
    }



    /**
     * Gets the license map for a specific organization.
     *
     * @param pOrganization the organization to look up
     * @return the organization's license map, or an empty map if the organization has no entries
     */
    @Nonnull
    Map<String, LicenseObject> getOrganizationMap(@Nonnull final Organization pOrganization)
    {
        return organizationMaps.getOrDefault(pOrganization, Collections.emptyMap());
    }



    /**
     * Gets all organization license maps.
     *
     * @return unmodifiable map of organization to their license maps
     */
    @Nonnull
    Map<Organization, Map<String, LicenseObject>> getOrganizationMaps()
    {
        return Collections.unmodifiableMap(organizationMaps);
    }
}
