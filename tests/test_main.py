#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of reuse.  It is copyrighted by the contributors recorded
# in the version control history of the file, available from its original
# location: https://git.fsfe.org/reuse/reuse
#
# reuse is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# reuse is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# reuse.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0+
# License-Filename: LICENSES/GPL-3.0.txt

"""Tests for the CLI for reuse."""

from itertools import zip_longest

import pytest
from reuse import _main, _util, __version__

# pylint: disable=invalid-name
git = pytest.mark.skipif(
    not _util.GIT_EXE,
    reason='requires git')


def test_lint_none(fake_repository, runner):
    """Given a repository in which every file is licensed, return an exit code
    of 0 and print nothing.
    """
    result = runner.invoke(_main.cli, ['lint', str(fake_repository)])

    assert not result.output
    assert result.exit_code == 0


@git
def test_lint_gitignore(git_repository, runner):
    """Given a repository with files ignored by Git, skip over those files."""
    result = runner.invoke(_main.cli, ['lint', str(git_repository)])

    assert not result.output
    assert result.exit_code == 0


def test_lint_ignore_debian(fake_repository, runner):
    """When debian/copyright is ignored, non-compliant files are found."""
    result = runner.invoke(
        _main.cli,
        ['--ignore-debian', 'lint', str(fake_repository)])

    output_lines = result.output.splitlines()
    assert len(output_lines) == 1
    assert 'no_license.py' in output_lines[0]
    assert result.exit_code


def test_compile(tiny_repository, runner):
    """A correct bill of materials is generated."""
    result = runner.invoke(
        _main.cli,
        ['compile'])

    expected = """SPDXVersion: SPDX-2.1
DataLicense: CC0-1.0
SPDXID: SPDXRef-DOCUMENT
DocumentName: {dirname}
DocumentNamespace: http://spdx.org/spdxdocs/spdx-v2.1-04c223f0-4415-47fd-9860-7074a07f753e
Creator: Person: Anonymous ()
Creator: Organization: Anonymous ()
Creator: Tool: reuse-{version}
Created: 2017-11-08T11:07:30
CreatorComment: <text>This document was created automatically using available license information consistent with the REUSE project.</text>
Relationship: SPDXRef-DOCUMENT describes SPDXRef-8008eeb8d2000e5aa6eaa51b1cdc944d726e1107
Relationship: SPDXRef-DOCUMENT describes SPDXRef-bb5656f1b5e8283a8e930c54afd9a8bfebe7a548

FileName: ./src/code.py
SPDXID: SPDXRef-8008eeb8d2000e5aa6eaa51b1cdc944d726e1107
FileChecksum: SHA1: d209e0212e7ecf809b6566aa59b1030dc69ae3a8
LicenseConcluded: NOASSERTION
LicenseInfoInFile: GPL-3.0
LicenseInfoInFile: LicenseRef-411cba51252f446399ab79a894958900a0ba444b
FileCopyrightText: NONE

FileName: ./src/no_license.py
SPDXID: SPDXRef-bb5656f1b5e8283a8e930c54afd9a8bfebe7a548
FileChecksum: SHA1: da39a3ee5e6b4b0d3255bfef95601890afd80709
LicenseConcluded: NOASSERTION
LicenseInfoInFile: CC0-1.0
FileCopyrightText: NONE

LicenseID: LicenseRef-411cba51252f446399ab79a894958900a0ba444b
LicenseName: NOASSERTION
ExtractedText: <text>GPL-3.0</text>""".format(
        dirname=tiny_repository.name,
        version=__version__)

    for result_line, expected_line in zip_longest(
            result.output.splitlines(),
            expected.splitlines()):
        # Just ignore these
        if 'DocumentNamespace' in result_line:
            continue
        if 'Created' in result_line:
            continue

        assert result_line == expected_line
