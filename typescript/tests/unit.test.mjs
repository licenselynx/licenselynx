/**
 * SPDX-FileCopyrightText: Copyright 2025 Siemens AG
 * SPDX-License-Identifier: BSD-3-Clause
 */
import assert from 'node:assert/strict';
import test from 'node:test';
import {
    LicenseSource,
    Organization,
    isCustomIdentifier,
    isOrganizationSource,
    isOrganizationSourceOf,
    isScancodeLicensedbIdentifier,
    isSpdxIdentifier,
    map,
} from '../dist/index.js';

test('should return data when license exists', () => {
    const licenseObject = map('BSD Zero Clause');
    assert.notEqual(licenseObject, null);
    assert.equal(licenseObject.id, '0BSD');
    assert.equal(licenseObject.src, 'spdx');
    assert.equal(licenseObject.src, LicenseSource.Spdx);
    assert.equal(isSpdxIdentifier(licenseObject), true);
    assert.equal(isScancodeLicensedbIdentifier(licenseObject), false);
});

test('should return Scancode LicenseDB data when license exists', () => {
    const licenseObject = map('License only in scancode');
    assert.notEqual(licenseObject, null);
    assert.equal(licenseObject.id, 'only-scancode');
    assert.equal(licenseObject.src, 'scancode-licensedb');
    assert.equal(licenseObject.src, LicenseSource.ScancodeLicensedb);
    assert.equal(isSpdxIdentifier(licenseObject), false);
    assert.equal(isScancodeLicensedbIdentifier(licenseObject), true);
});

test('should return custom source when license exists', () => {
    const licenseObject = map('Custom License');
    assert.notEqual(licenseObject, null);
    assert.equal(licenseObject.id, 'custom-license');
    assert.equal(licenseObject.src, 'custom');
    assert.equal(licenseObject.src, LicenseSource.Custom);
    assert.equal(isSpdxIdentifier(licenseObject), false);
    assert.equal(isScancodeLicensedbIdentifier(licenseObject), false);
    assert.equal(isCustomIdentifier(licenseObject), true);
});

test('should return normalized quotes when license exists', () => {
    const licenseObject = map('BSD \u201AZero\u201B Clause');
    assert.notEqual(licenseObject, null);
    assert.equal(licenseObject.id, '0BSD');
    assert.equal(licenseObject.src, 'spdx');
});

test('should return data when license exists in risky map', () => {
    const licenseObject = map('BSD Zero Clause Risky', true);
    assert.notEqual(licenseObject, null);
    assert.equal(licenseObject.id, '0BSD');
    assert.equal(licenseObject.src, 'spdx');
});

test('should return reject error when license not found', () => {
    assert.throws(() => map('licenseNonExisting'), new Error('License licenseNonExisting not found.'));
    assert.throws(() => map('licenseNonExisting', true), new Error('License licenseNonExisting not found.'));
});

test('should return reject error when input is null', () => {
    assert.throws(() => map(null), new Error('License null not found.'));
    assert.throws(() => map(null, true), new Error('License null not found.'));
});

test('should reject when organization license does not exist', () => {
    assert.throws(
        () => map('nonExistingOrgLicense', false, Organization.Siemens),
        new Error('License nonExistingOrgLicense not found.'),
    );
});

test('should return false for isOrganizationSource on spdx license', () => {
    const licenseObject = map('BSD Zero Clause');
    assert.equal(isOrganizationSource(licenseObject), false);
    assert.equal(isOrganizationSourceOf(licenseObject, Organization.Siemens), false);
});

test('should reject when organization map does not exist in data', () => {
    assert.throws(
        () => map('test-org-license', false, 'unknown-org'),
        new Error('License test-org-license not found.'),
    );
});

test('should reject when license data has empty id', () => {
    assert.throws(() => map('Incomplete License'), new Error('License Incomplete License not found.'));
});
