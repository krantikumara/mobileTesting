"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, XML, CAT, TR, TD
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from datetime import datetime
from py4web.utils.publisher import Publisher, ALLOW_ALL_POLICY
import xmlrpc.client


@action("index")
@action.uses(flash,"index.html")
def execution_summary():
    return dict()

@action("api/get_execution_summary", method='GET')
def fetch_execution_summary():
    items = []
    for row in db(db.execution_results.id > 0).select():
        if not "total_tests" in row.execution_data:
            # This means not even 1 TC got reported.
            # We return empty data in this case
            # To-Do: Improve user experience by implementing loaders in UI
            continue
        items.append({"execution_id":row.execution_id,
                      "execution_name":row.execution_name,
                      "total":row.execution_data["total_tests"],
                      "passed":row.execution_data["total_passed"],
                      "failed":row.execution_data["total_failed"]})
        
    return dict(items=items)

@action("api/get_execution_details")
def fetch_execution_details():
    exec_id = request.query["execution_id"]
    execution_row = db(db.execution_results.execution_id == exec_id).select().first()
    if not execution_row:
        return dict()
    
    execution_row.execution_data
    
    return dict(data=execution_row.execution_data)


@action('api/execution/report_test', method='POST')
def record_execution():
    if "execution_id" in request.headers:
        exec_id = request.headers["execution_id"]
    else:
        return dict()
    tc_id = request.json["testcase_id"]
    
    execution_row = db(db.execution_results.execution_id == exec_id).select().first()
    if not execution_row:
        return dict()
    
    json_data = execution_row.execution_data
    
    json_data["end-time"] = request.json["timestamp"]
    
    tc_status = "PASSED"
    if tc_id in json_data["steps"]:
        for step in json_data["steps"][tc_id]:
            if step["passed"] == False:
                tc_status = "FAILED"
    
    # Update tc-id in tests list along with end-time and status
    if tc_id in json_data["tests"]:
        json_data["tests"][tc_id]["end_time"] = request.json["timestamp"]
        json_data["tests"][tc_id]["status"] = tc_status

    # Update the overall execution state as well
    count_passed = 0
    count_failed = 0
    for test in json_data["tests"]:
        if json_data["tests"][test]["status"] == "PASSED":
            count_passed += 1
        else:
            count_failed += 1
    
    json_data["total_passed"] = count_passed
    json_data["total_failed"] = count_failed
    json_data["total_tests"] = count_failed + count_passed
    
    execution_row.update_record(execution_data=json_data)
    
    db.commit()
    return dict()

@action('api/execution/report_execution_step', method='POST')
def record_step():
    if "execution_id" in request.headers:
        exec_id = request.headers["execution_id"]
    else:
        return dict()
    tc_id = request.json["testcase_id"]
    
    execution_row = db(db.execution_results.execution_id == exec_id).select().first()
    if not execution_row:
        return dict()
    
    json_data = execution_row.execution_data
    
    if tc_id in json_data["steps"]:
        json_data["steps"][tc_id].append(request.json)
    else:
        json_data["steps"][tc_id] = [request.json]
    
    # Check if tc-id already exists in tests list if not
    # Add tc-id to tests list along with start-time
    if tc_id not in json_data["tests"]:
        json_data["tests"][tc_id] = {}
        json_data["tests"][tc_id]["start_time"] = request.json["timestamp"]
        json_data["tests"][tc_id]["status"] = "IN-PROGRESS"
        
    execution_row.update_record(execution_data=json_data)
    
    db.commit()
    return dict()
    
@action('api/execution/report_driver_log', method='POST')
def record_driver_log():
    if "execution_id" in request.headers:
        exec_id = request.headers["execution_id"]
    else:
        return dict()
    tc_id = request.json["testcase_id"]
    
    execution_row = db(db.execution_results.execution_id == exec_id).select().first()
    if not execution_row:
        return dict()
    
    json_data = execution_row.execution_data
    
    if tc_id in json_data["driver_logs"]:
        json_data["driver_logs"][tc_id].append(request.json)
    else:
        json_data["driver_logs"][tc_id] = [request.json]
        
    execution_row.update_record(execution_data=json_data)
    
    db.commit()
    return dict()
    
@action('api/execution/get_execution_id', method='POST')
def register_execution():
    if "execution_id" in request.json:
        exec_id = request.json["execution_id"]
    else:
        return 401, dict()

    current_timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    execution_name = "TestRun_" + current_timestamp
    execution_data = {"execution_id":exec_id,
                      "execution_name":execution_name,
                      "start_time": current_timestamp,
                      "steps":{}, "tests":{}, "driver_logs":{}}
    
    db.execution_results.insert(execution_id=exec_id, 
                                execution_name=execution_name, 
                                execution_data=execution_data)
    db.commit()
    print("Registering execution with id :" + exec_id)
    return dict(execution_id=exec_id)


#TestRunner interactions
#To-Do: Move this to a different controller file

@action('api/test_planner/get_test_suites', method='GET')
def get_test_suites():
    test_runner = xmlrpc.client.ServerProxy('http://localhost:8001')
    suites = test_runner.get_test_suites()
    return dict(suites=suites)
    
    
@action('api/test_planner/get_suite_details')
def get_suite_details():
    suite_id = request.query["suite"]
    test_runner = xmlrpc.client.ServerProxy('http://localhost:8001')
    tests = test_runner.get_tests(suite_id)
    return dict(tests=tests)
    
@action('api/test_planner/run_test')
@action.uses(flash)
def get_suite_details():
    test_id = request.query["test_id"]
    test_runner = xmlrpc.client.ServerProxy('http://localhost:8001')
    status = test_runner.run_test(test_id)
    if status:
        flash.set("Successfully triggered run: " + test_id, sanitize=True)
    else:
        flash.set("Failed to trigger run: " + test_id, sanitize=True)

    return dict(status=status)



