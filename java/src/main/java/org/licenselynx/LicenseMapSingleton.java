/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import javax.annotation.Nonnull;
import java.util.Objects;


/**
 * Singleton class that manages a mapping of licenses.
 */
class LicenseMapSingleton
{
    private final LicenseMap licenseMap;

    private static LicenseMapSingleton instance;



    /**
     * Package-private constructor for test injection.
     *
     * @param pLicenseMap the license map to use (must not be null)
     */
    LicenseMapSingleton(@Nonnull final LicenseMap pLicenseMap)
    {
        this.licenseMap = Objects.requireNonNull(pLicenseMap, "licenseMap cannot be null");
    }



    /**
     * Private constructor for normal usage.
     * Loads license data and prevents multiple instantiations.
     */
    private LicenseMapSingleton()
    {
        if (instance != null)
        {
            throw new InstantiationError("Instance already exists!");
        }

        this.licenseMap = new LicenseDataLoader().loadLicenses();
    }



    /**
     * Returns the singleton instance of {@code LicenseMapSingleton}.
     *
     * @return the singleton instance (never null)
     */
    @Nonnull
    static synchronized LicenseMapSingleton getInstance()
    {
        if (instance == null)
        {
            instance = new LicenseMapSingleton();
        }
        return instance;
    }



    /**
     * Returns the license map.
     *
     * @return a non-null map containing license mappings
     */
    @Nonnull
    LicenseMap getLicenseMap()
    {
        return licenseMap;
    }
}

