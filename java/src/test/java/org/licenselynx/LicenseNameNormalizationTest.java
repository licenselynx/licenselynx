/*
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
package org.licenselynx;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DynamicTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestFactory;


/**
 * Runs the shared normalization spec (fixtures/normalization.json) against
 * {@link LicenseLynx#normalizeLicenseName(String)}.
 */
public class LicenseNameNormalizationTest
{
    private static JsonObject loadSpec() throws IOException
    {
        String content = new String(Files.readAllBytes(Paths.get("..", "fixtures", "normalization.json")),
            StandardCharsets.UTF_8);
        return JsonParser.parseString(content).getAsJsonObject();
    }



    @TestFactory
    public List<DynamicTest> testCases() throws IOException
    {
        List<DynamicTest> tests = new ArrayList<>();
        for (JsonElement element : loadSpec().getAsJsonArray("testCases"))
        {
            JsonObject testCase = element.getAsJsonObject();
            String input = testCase.get("input").getAsString();
            String expected = testCase.get("expected").getAsString();
            tests.add(DynamicTest.dynamicTest(testCase.get("name").getAsString(),
                () -> Assertions.assertEquals(expected, LicenseLynx.normalizeLicenseName(input))));
        }
        return tests;
    }



    @TestFactory
    public List<DynamicTest> testEveryQuoteCharacter() throws IOException
    {
        JsonObject spec = loadSpec();
        String replacement = spec.get("quoteReplacement").getAsString();
        List<DynamicTest> tests = new ArrayList<>();
        for (JsonElement element : spec.getAsJsonArray("quoteCharacters"))
        {
            String quote = element.getAsString();
            String input = "a" + quote + "b";
            String expected = "a" + replacement + "b";
            tests.add(DynamicTest.dynamicTest(String.format("U+%04X", quote.codePointAt(0)),
                () -> Assertions.assertEquals(expected, LicenseLynx.normalizeLicenseName(input))));
        }
        return tests;
    }



    @TestFactory
    public List<DynamicTest> testEveryTrimCharacter() throws IOException
    {
        List<DynamicTest> tests = new ArrayList<>();
        for (JsonElement element : loadSpec().getAsJsonArray("trimCharacters"))
        {
            String trim = element.getAsString();
            tests.add(DynamicTest.dynamicTest(String.format("U+%04X", trim.codePointAt(0)),
                () -> Assertions.assertEquals("a", LicenseLynx.normalizeLicenseName(trim + "a" + trim))));
        }
        return tests;
    }



    @Test
    @SuppressWarnings("ConstantValue")
    public void testNullInput()
    {
        Assertions.assertNull(LicenseLynx.normalizeLicenseName(null));
    }
}
