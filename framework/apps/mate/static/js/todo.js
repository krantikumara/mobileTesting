// initialize the app
var myapp = Q.app();
// data exposed to the view
myapp.api = '/' + window.location.href.split('/')[3] + '/api/';
myapp.data.items = [];
myapp.data.show_execution_results = false
myapp.data.show_execution_summary = false
myapp.data.show_test_step_results = false
myapp.data.show_test_suites = false
myapp.data.show_suite_details = false
myapp.data.step_data = {}
myapp.data.tc_step_data = []

myapp.data.suites = []
myapp.data.suite_tests = []

// methods exposed to the view

myapp.methods.details = function(item_id) { 

    axios.get(myapp.api + 'get_execution_details?execution_id=' + item_id).then(function(res){
                    myapp.v.exec_data = res.data.data.tests;
                    myapp.v.step_data = res.data.data.steps;
                    myapp.v.show_execution_results = true;
                    myapp.v.show_execution_summary = false;
        });
};

myapp.methods.suite_details = function(item_id) {
    axios.get(myapp.api + 'test_planner/get_suite_details?suite=' + item_id).then(function(res){
                    myapp.v.suite_tests = res.data.tests;
                    myapp.v.show_suite_details = true
                    myapp.v.show_test_suites = false;
        });
};

myapp.methods.tc_details = function(item_id) { 
                    console.log(item_id);
                    myapp.v.show_execution_results = false;
                    myapp.v.show_execution_summary = false;
                    myapp.v.show_test_step_results = true;
                    for (var property in myapp.v.step_data) {
                        if (property === item_id) {
                            myapp.v.tc_step_data = myapp.v.step_data[property]
                            console.log(myapp.v.step_data[property]);
                        }
                    }
};

myapp.methods.run_test = function(item_id) { 
                    axios.get(myapp.api + 'test_planner/run_test?test_id=' + item_id).then(function(res){
                    var redirect_to =  '/' + window.location.href.split('/')[3] + '/index';
                    window.location.href = redirect_to;
        });
};


// start the app
myapp.start();
axios.get(myapp.api + 'get_execution_summary').then(function(res){
        myapp.v.items = res.data.items;
        myapp.v.show_execution_results = false;
        myapp.v.show_test_step_results = false;
        if (myapp.v.items.length > 0) {
            myapp.v.show_execution_summary = true;
        }
    });
    
axios.get(myapp.api + 'test_planner/get_test_suites').then(function(res){
        myapp.v.suites = res.data.suites;
        if (myapp.v.suites.length > 0) {
            myapp.v.show_test_suites = true;
        }
    });
