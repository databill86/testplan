"""TODO."""

import re

import pytest

from testplan.common.utils.exceptions import should_raise
from testplan.common.utils.interface import MethodSignatureMismatch
from testplan.common.utils.strings import format_description
from testplan.testing.multitest.suite import (testcase, testsuite, skip_if,
                                              post_testcase, pre_testcase)


def ptestcase(name, self, env, result, **kwargs):
    pass


@pre_testcase(ptestcase)
@post_testcase(ptestcase)
@testsuite
class MySuite1(object):
    @testcase
    def case1(self, env, result):
        pass

    @skip_if(lambda suite: True)
    @testcase
    def case2(self, env, result):
        pass

    @testcase
    def case3(self, env, result):
        pass


@testsuite(tags='A')
class MySuite2(object):
    @testcase(tags='B')
    def case1(self, env, result):
        pass

    @skip_if(lambda suite: True)
    @testcase(tags={'c': 'C'})
    def case2(self, env, result):
        pass

    @testcase(tags={'d': ['D1', 'D2']})
    def case3(self, env, result):
        pass


@testsuite
class MySuite3(object):
    @testcase(parameters=(1, 2, 3))
    def case(self, env, result, param):
        pass


def test_basic_suites():
    mysuite = MySuite1()
    cases = ('case1', 'case2', 'case3')
    assert tuple(mysuite.__testcases__) == cases
    assert tuple(mysuite.__skip__) == ('case2',)
    for case, meth in mysuite.get_testcase_methods().items():
        assert case in cases
        assert callable(meth)
    for case, meth in mysuite.get_testcases().items():
        assert case in cases
        assert callable(meth)


def test_basic_parametrization():
    mysuite = MySuite3()
    cases = ('case__param_1', 'case__param_2', 'case__param_3')
    assert tuple(mysuite.__testcases__) == cases
    for case, meth in mysuite.get_testcase_methods().items():
        assert case in cases
        assert callable(meth)


def test_basic_suite_tags():
    mysuite = MySuite2()
    assert mysuite.__TAGS__ == {'simple': frozenset(['A'])}
    case_dict = {'case1': {'simple': frozenset(['B'])},
                 'case2': {'c': frozenset(['C'])},
                 'case3': {'d': frozenset(['D2', 'D1'])}}
    for case, meth in mysuite.get_testcase_methods().items():
        assert meth.tags == case_dict[case]


def incorrent_case_signature1():
    @testsuite
    class _(object):
        @testcase
        def case1(self, envs, result):
            pass


def incorrent_case_signature2():
    @testsuite
    class _(object):
        @testcase
        def case1(self, env, results):
            pass


def test_testcase_signature():
    pattern = re.compile((r'.*Expected case1\(self, env, result\), '
                          'not case1\(self, envs, result\).*'))
    should_raise(MethodSignatureMismatch, incorrent_case_signature1,
                 pattern=pattern)
    pattern = re.compile((r'.*Expected case1\(self, env, result\), '
                          'not case1\(self, env, results\).*'))
    should_raise(MethodSignatureMismatch, incorrent_case_signature2,
             pattern=pattern)


def incorrent_skip_if_signature1():
    @testsuite
    class _(object):
        @skip_if(lambda _: True)
        @testcase
        def case1(self, env, result):
            pass


def test_skip_if_signature():
    pattern = re.compile(r'.*Expected <lambda>\(suite\), not <lambda>\(_\).*')
    should_raise(MethodSignatureMismatch, incorrent_skip_if_signature1,
                 pattern=pattern)


@pytest.mark.parametrize(
    'text,expected',
    (
          ('', ''),
          ('foo', 'foo'),
          ('  foo', 'foo'),
          ('foo', 'foo'),
          ('  foo  \n    bar\n\n', '  foo\n  bar'),
          ('\t\tfoo  \n   bar\n\n', '  foo\n bar'),
          (u'  foo\n    bar\n\n', u'  foo\nbar'),
    )
)
def test_format_description(text, expected):
    format_description(text) == expected
