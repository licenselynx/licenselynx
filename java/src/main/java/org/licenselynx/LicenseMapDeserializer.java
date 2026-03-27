/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.EnumMap;
import java.util.Iterator;
import java.util.Map;


/**
 * Custom Jackson deserializer for {@link LicenseMap}.
 * Handles the fixed keys "stableMap" and "riskyMap", and dynamically resolves
 * any other top-level keys as {@link Organization} maps.
 */
class LicenseMapDeserializer extends JsonDeserializer<LicenseMap>
{
    private static final String STABLE_MAP_KEY = "stableMap";
    private static final String RISKY_MAP_KEY = "riskyMap";
    private static final TypeReference<Map<String, LicenseObject>> MAP_TYPE_REF =
        new TypeReference<Map<String, LicenseObject>>() {};


    @Override
    public LicenseMap deserialize(final JsonParser pParser, final DeserializationContext pContext)
        throws IOException
    {
        ObjectMapper mapper = (ObjectMapper) pParser.getCodec();
        JsonNode rootNode = mapper.readTree(pParser);

        // Deserialize the fixed maps
        Map<String, LicenseObject> stableMap = mapper.convertValue(rootNode.get(STABLE_MAP_KEY), MAP_TYPE_REF);
        Map<String, LicenseObject> riskyMap = mapper.convertValue(rootNode.get(RISKY_MAP_KEY), MAP_TYPE_REF);

        // Deserialize organization maps
        Map<Organization, Map<String, LicenseObject>> orgMaps = new EnumMap<>(Organization.class);
        Iterator<String> fieldNames = rootNode.fieldNames();
        while (fieldNames.hasNext())
        {
            String fieldName = fieldNames.next();
            if (STABLE_MAP_KEY.equals(fieldName) || RISKY_MAP_KEY.equals(fieldName))
            {
                continue;
            }

            // Check if this field name corresponds to an Organization
            for (Organization org : Organization.values())
            {
                if (org.getValue().equals(fieldName))
                {
                    Map<String, LicenseObject> orgMap = mapper.convertValue(rootNode.get(fieldName), MAP_TYPE_REF);
                    orgMaps.put(org, orgMap);
                    break;
                }
            }
        }

        return new LicenseMap(stableMap, riskyMap, orgMaps);
    }
}
