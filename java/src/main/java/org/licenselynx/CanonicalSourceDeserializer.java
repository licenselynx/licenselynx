/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;

import java.io.IOException;

/**
 * Custom Jackson deserializer for {@link CanonicalSource}.
 * Attempts to resolve the JSON string value first as a {@link LicenseSource},
 * then as an {@link Organization}.
 */
class CanonicalSourceDeserializer extends JsonDeserializer<CanonicalSource>
{
    @Override
    public CanonicalSource deserialize(final JsonParser pParser, final DeserializationContext pContext)
        throws IOException
    {
        return fromValue(pParser.getText());
    }

    /**
     * Parses a string value to a CanonicalSource.
     * Tries LicenseSource first, then Organization.
     *
     * @param pValue The string value to parse.
     * @return The corresponding CanonicalSource.
     * @throws IllegalArgumentException if the value is unknown.
     */
    static CanonicalSource fromValue(final String pValue)
    {
        // Try LicenseSource first
        for (LicenseSource source : LicenseSource.values())
        {
            if (source.getValue().equals(pValue))
            {
                return source;
            }
        }

        // Try Organization
        for (Organization org : Organization.values())
        {
            if (org.getValue().equals(pValue))
            {
                return org;
            }
        }

        throw new IllegalArgumentException("Unknown canonical source: " + pValue);
    }
}
