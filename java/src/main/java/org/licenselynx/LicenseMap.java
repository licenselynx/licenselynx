/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import net.jcip.annotations.Immutable;

import javax.annotation.Nonnull;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;


/**
 * LicenseMap represents the two JSON Objects for the canonical license map and the risky license map
 * It provides getters to access these properties.
 */
@Immutable
class LicenseMap
{
    private final Map<String, Map<String, LicenseObject>> licenseMaps;



    @JsonCreator
    public LicenseMap(final Map<String, Map<String, LicenseObject>> pLicenseMaps)
    {
        this.licenseMaps = Objects.requireNonNull(pLicenseMaps);
    }



    /**
     * Gets the canonical license map.
     * @return canonical license map
     */
    @Nonnull
    public Map<String, LicenseObject> getCanonicalLicenseMap()
    {
        return licenseMaps.getOrDefault("stableMap", new HashMap<>());
    }



    /**
     * Gets the risky license map.
     * @return risky license map
     */
    @Nonnull
    public Map<String, LicenseObject> getRiskyLicenseMap()
    {
        return licenseMaps.getOrDefault("riskyMap", new HashMap<>());
    }



    /**
     * Gets the license map for a specific extra organization.
     * @param pExtra the organization enum
     * @return the license map, or null if not found
     */
    @CheckForNull
    public Map<String, LicenseObject> getMap(final Extra pExtra)
    {
        if (pExtra == null)
        {
            return getCanonicalLicenseMap();
        }

        // The key is the lowercase name of the enum + "Map"
        return licenseMaps.get(pExtra.name().toLowerCase() + "Map");
    }
}
