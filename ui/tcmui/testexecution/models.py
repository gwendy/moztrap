"""
Remote objects related to the "documentation" (as opposed to execution) side of
testing.

"""
from django.core.urlresolvers import reverse

from ..core.api import Activatable, RemoteObject, ListObject, fields
from ..environments.models import EnvironmentGroupList, EnvironmentList
from ..products.models import Product
from ..static.fields import StaticData
from ..testcases.models import (
    TestCase, TestCaseVersion, TestSuite, TestSuiteIncludedTestCase)
from ..users.models import User, Team

from . import testresultstatus



class TestCycle(Activatable, RemoteObject):
    product = fields.Locator(Product)
    name = fields.Field()
    description = fields.Field()
    testCycleStatus = StaticData("TESTCYCLESTATUS")
    startDate = fields.Date()
    endDate = fields.Date()

    environmentgroups = fields.Link(EnvironmentGroupList)
    testruns = fields.Link("TestRunList")
    team = fields.Link(Team, api_name="team/members")


    def __unicode__(self):
        return self.name


    def get_absolute_url(self):
        return reverse(
            "testruns",
            kwargs={"cycle_id": self.id})


    def approveallresults(self, **kwargs):
        self._put(
            relative_url="approveallresults",
            **kwargs)



class TestCycleList(ListObject):
    entryclass = TestCycle
    api_name = "testcycles"
    default_url = "testcycles"

    entries = fields.List(fields.Object(TestCycle))



class TestRun(Activatable, RemoteObject):
    product = fields.Locator(Product)
    testCycle = fields.Locator(TestCycle)
    name = fields.Field()
    description = fields.Field()
    testRunStatus = StaticData("TESTRUNSTATUS")
    selfAssignAllowed = fields.Field()
    selfAssignLimit = fields.Field()
    selfAssignPerEnvironment = fields.Field()
    useLatestVersions = fields.Field()
    autoAssignToTeam = fields.Field()
    startDate = fields.Date()
    endDate = fields.Date()

    environmentgroups = fields.Link(EnvironmentGroupList)
    includedtestcases = fields.Link("TestRunIncludedTestCaseList")
    team = fields.Link(Team, api_name="team/members")


    def __unicode__(self):
        return self.name


    def get_absolute_url(self):
        return reverse("runtests", kwargs={"testrun_id": self.id})


    def addcase(self, case, **kwargs):
        payload = {
            "testCaseVersionId": case.id,
            "priorityId": 0, # @@@
            "runOrder": 0, # @@@
            }
        self._post(
            relative_url="includedtestcases",
            extra_payload=payload,
            **kwargs)


    def addsuite(self, suite, **kwargs):
        self._post(
            relative_url="includedtestcases/testsuite/%s/" % suite.id,
            **kwargs)


    def approveallresults(self, **kwargs):
        self._put(
            relative_url="approveallresults",
            **kwargs)



class TestRunList(ListObject):
    entryclass = TestRun
    api_name = "testruns"
    default_url = "testruns"

    entries = fields.List(fields.Object(TestRun))



class TestRunIncludedTestCase(TestSuiteIncludedTestCase):
    testRun = fields.Locator(TestRun)

    assignments = fields.Link("TestCaseAssignmentList")

    def assign(self, tester, **kwargs):
        payload = {"testerId": tester.id}
        assignment = TestCaseAssignment()
        self._post(
            relative_url="assignments",
            extra_payload=payload,
            update_from_response=assignment,
            **kwargs)
        assignment.auth = self.auth
        return assignment



class TestRunIncludedTestCaseList(ListObject):
    entryclass = TestRunIncludedTestCase
    api_name = "includedtestcases"
    array_name = "includedtestcase"
    default_url = "testruns/includedtestcases"

    entries = fields.List(fields.Object(TestRunIncludedTestCase))



class TestCaseAssignment(RemoteObject):
    product = fields.Locator(Product)
    testCase = fields.Locator(TestCase)
    testCaseVersion = fields.Locator(TestCaseVersion)
    testSuite = fields.Locator(TestSuite)
    tester = fields.Locator(User)
    testRun = fields.Locator(TestRun)

    environmentgroups = fields.Link(EnvironmentGroupList)
    results = fields.Link("TestResultList")

    def __unicode__(self):
        return self.id



class TestCaseAssignmentList(ListObject):
    entryclass = TestCaseAssignment
    api_name = "testcaseassignments"
    default_url = "testruns/assignments"

    entries = fields.List(fields.Object(TestCaseAssignment))



class TestResult(RemoteObject):
    actualResult = fields.Field()
    actualTimeInMin = fields.Field()
    approvalStatus = StaticData("APPROVALSTATUS", api_submit_name=False)
    approvedBy = fields.Locator(User, api_submit_name=False)
    comment = fields.Field()
    failedStepNumber = fields.Field()
    product = fields.Locator(Product)
    testCase = fields.Locator(TestCase)
    testCaseVersion = fields.Locator(TestCaseVersion)
    testSuite = fields.Locator(TestSuite)
    testRun = fields.Locator(TestRun)
    testRunResultStatus = StaticData("TESTRUNRESULTSTATUS", api_submit_name=False)
    tester = fields.Locator(User)

    environments = fields.Link(EnvironmentList)


    def __unicode__(self):
        return self.id


    def start(self, **kwargs):
        self._put(
            relative_url="start",
            update_from_response=True,
            **kwargs)


    def approve(self, **kwargs):
        self._put(
            relative_url="approve",
            update_from_response=True,
            **kwargs)


    def finishsucceed(self, **kwargs):
        self._put(
            relative_url="finishsucceed",
            update_from_response=True,
            **kwargs)


    def finishinvalidate(self, comment, **kwargs):
        self._put(
            relative_url="finishinvalidate",
            extra_payload={"comment": comment},
            update_from_response=True,
            **kwargs)


    def finishfail(self, failedStepNumber, actualResult, **kwargs):
        self._put(
            relative_url="finishfail",
            extra_payload={
                "failedStepNumber": failedStepNumber,
                "actualResult": actualResult
                },
            update_from_response=True,
            **kwargs)


    def reject(self, comment, **kwargs):
        self._put(
            relative_url="reject",
            extra_payload={"comment": comment},
            update_from_response=True,
            **kwargs)


    @property
    def pending(self):
        return self.testRunResultStatus.id == testresultstatus.PENDING


    @property
    def started(self):
        return self.testRunResultStatus.id == testresultstatus.STARTED


    @property
    def passed(self):
        return self.testRunResultStatus.id == testresultstatus.PASSED


    @property
    def invalidated(self):
        return self.testRunResultStatus.id == testresultstatus.INVALIDATED


    @property
    def failed(self):
        return self.testRunResultStatus.id == testresultstatus.FAILED



class TestResultList(ListObject):
    entryclass = TestResult
    api_name = "testresults"
    default_url = "testruns/results"

    entries = fields.List(fields.Object(TestResult))
