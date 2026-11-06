// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

type normalizationSpec struct {
	QuoteReplacement string   `json:"quoteReplacement"`
	QuoteCharacters  []string `json:"quoteCharacters"`
	TrimCharacters   []string `json:"trimCharacters"`
	TestCases        []struct {
		Name     string `json:"name"`
		Input    string `json:"input"`
		Expected string `json:"expected"`
	} `json:"testCases"`
	MappingCases []struct {
		Name  string  `json:"name"`
		Input string  `json:"input"`
		Risky bool    `json:"risky"`
		Org   string  `json:"org"`
		ID    *string `json:"id"`
		Src   string  `json:"src"`
	} `json:"mappingCases"`
}

func loadNormalizationSpec(t *testing.T) normalizationSpec {
	t.Helper()

	content, err := os.ReadFile(filepath.Join("..", "fixtures", "normalization.json"))
	if err != nil {
		t.Fatalf("read normalization spec: %v", err)
	}

	var spec normalizationSpec
	if err := json.Unmarshal(content, &spec); err != nil {
		t.Fatalf("parse normalization spec: %v", err)
	}

	return spec
}

func TestNormalizeLicenseNameCases(t *testing.T) {
	t.Parallel()

	spec := loadNormalizationSpec(t)

	for _, testCase := range spec.TestCases {
		t.Run(testCase.Name, func(t *testing.T) {
			t.Parallel()
			if got := normalizeLicenseName(testCase.Input); got != testCase.Expected {
				t.Fatalf("normalizeLicenseName(%q) = %q, want %q", testCase.Input, got, testCase.Expected)
			}
		})
	}
}

func TestNormalizeLicenseNameEveryQuoteCharacter(t *testing.T) {
	t.Parallel()

	spec := loadNormalizationSpec(t)

	for _, quote := range spec.QuoteCharacters {
		t.Run(fmt.Sprintf("%U", []rune(quote)[0]), func(t *testing.T) {
			t.Parallel()
			if got, want := normalizeLicenseName("a"+quote+"b"), "a"+spec.QuoteReplacement+"b"; got != want {
				t.Fatalf("got %q, want %q", got, want)
			}
		})
	}
}

func TestSharedCaseInsensitiveMappings(t *testing.T) {
	t.Parallel()

	for _, testCase := range loadNormalizationSpec(t).MappingCases {
		t.Run(testCase.Name, func(t *testing.T) {
			t.Parallel()
			var opts []Option
			if testCase.Risky {
				opts = append(opts, WithRisky())
			}
			if testCase.Org != "" {
				opts = append(opts, WithOrganization(Organization(testCase.Org)))
			}
			got, ok := Map(testCase.Input, opts...)
			if testCase.ID == nil {
				if ok || got != (LicenseObject{}) {
					t.Fatalf("expected no match, got %+v ok=%v", got, ok)
				}
			} else if !ok || got.ID != *testCase.ID || got.Src != testCase.Src {
				t.Fatalf("got %+v ok=%v, want ID=%q Src=%q", got, ok, *testCase.ID, testCase.Src)
			}
		})
	}
}

func TestNormalizeLicenseNameEveryTrimCharacter(t *testing.T) {
	t.Parallel()

	spec := loadNormalizationSpec(t)

	for _, char := range spec.TrimCharacters {
		t.Run(fmt.Sprintf("%U", []rune(char)[0]), func(t *testing.T) {
			t.Parallel()
			if got := normalizeLicenseName(char + "a" + char); got != "a" {
				t.Fatalf("got %q, want %q", got, "a")
			}
		})
	}
}

func TestMapTrimsSurroundingWhitespace(t *testing.T) {
	t.Parallel()

	testMaps := licenseMaps{
		stable: map[string]LicenseObject{"mit": {ID: "MIT", Src: string(SourceSPDX)}},
	}

	got, ok := mapWithLicenseMaps("  \tMIT \r\n", testMaps)
	if !ok || got.ID != "MIT" {
		t.Fatalf("expected MIT after trimming, got %+v ok=%v", got, ok)
	}
}
