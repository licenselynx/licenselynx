/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import * as mergedData from './resources/merged_data.json';

export interface LicenseObject {
    readonly id: string;
    readonly src: LicenseSource;
}

export interface LicenseMap {
    [licenseName: string]: LicenseObject;
}

export enum LicenseSource {
    Spdx = 'spdx',
    ScancodeLicensedb = 'scancode-licensedb',
    Custom = 'custom',
}

export enum Extra {
}

interface LicenseRepository {
    stableMap: LicenseMap;
    riskyMap: LicenseMap;
    [extraMap: string]: LicenseMap;
}


/**
 * Returns the license map for the given extra organization.
 * @param licenses the merged license repository
 * @param extra the organization enum
 * @returns the organization's license map, or undefined if not found
 */
const getExtraMap = function (licenses: LicenseRepository, extra: Extra): LicenseMap | undefined {
    return licenses[`${extra}Map` as keyof LicenseRepository] as LicenseMap | undefined;
};


/**
 * Maps the given license name to its corresponding LicenseObject.
 *
 * @param licenseName the name of the license to map
 * @param risky if true, also search in the risky map
 * @param extra enable extra mappings for a specific company/org
 * @returns LicenseObject as promise or error if not found
 */
export const map = function (licenseName: string, risky: boolean = false, extra: Extra | null = null) {
    return new Promise<LicenseObject>((resolve, reject) => {
        const licenses = mergedData as LicenseRepository;

        const normalizedLicenseName = normalizeQuotes(licenseName);

        let licenseData = licenses.stableMap[normalizedLicenseName];

        if (!licenseData && risky) {
            licenseData = licenses.riskyMap[licenseName];
        }

        if (!licenseData && extra) {
            const extraMap = getExtraMap(licenses, extra);
            if (extraMap) {
                licenseData = extraMap[normalizedLicenseName];
            }
        }

        if (licenseData) {
            const canonical = licenseData.id;
            const src = licenseData.src;

            if (canonical && src) {
                resolve(Object.freeze({ id: canonical, src }));
            }
        }

        reject(new Error('License ' + licenseName + ' not found.'));
    })
}

export const isSpdxIdentifier = function (licenseObject: LicenseObject): boolean {
    return licenseObject.src === LicenseSource.Spdx;
}

export const isScancodeLicensedbIdentifier = function (licenseObject: LicenseObject): boolean {
    return licenseObject.src === LicenseSource.ScancodeLicensedb;
}

export const isCustomIdentifier = function (licenseObject: LicenseObject): boolean {
    return licenseObject.src === LicenseSource.Custom;
}


// A readonly array of quote characters to be replaced.
const QUOTE_CHARACTERS: readonly string[] = [
    // Single quotes
    '‘', // LEFT SINGLE QUOTATION MARK
    '’', // RIGHT SINGLE QUOTATION MARK
    '‚', // SINGLE LOW-9 QUOTATION MARK
    '‛', // SINGLE HIGH-REVERSED-9 QUOTATION MARK
    '′', // PRIME (often used as an apostrophe)
    '＇', // FULLWIDTH APOSTROPHE
    // Double quotes
    '“', // LEFT DOUBLE QUOTATION MARK
    '”', // RIGHT DOUBLE QUOTATION MARK
    '„', // DOUBLE LOW-9 QUOTATION MARK
    '‟', // DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    '″', // DOUBLE PRIME
    '«', // LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    '»', // RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    '＂'  // FULLWIDTH QUOTATION MARK
];

/**
 * Checks if a given character is a recognized quote character.
 *
 * @param char - The character to check.
 * @returns True if the character is a quote character, false otherwise.
 */
const isQuoteCharacter = (char: string): boolean => {
    return QUOTE_CHARACTERS.includes(char);
};

/**
 * Normalizes an input string by replacing recognized Unicode quote characters
 * with a specified replacement string.
 *
 * @param input - The input string that may contain various quote characters.
 * @param replacement - The string to replace the quote characters. Defaults to "'".
 * @returns The normalized string with replaced quote characters.
 */
const normalizeQuotes = (input: string, replacement: string = "'"): string => {
    if (!input) return input;

    return input
        .split("")
        .map(char => isQuoteCharacter(char) ? replacement : char)
        .join("");
};


