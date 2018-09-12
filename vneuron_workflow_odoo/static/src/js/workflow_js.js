odoo.define('vneuron_workflow_odoo.data', function (require) {
    "use strict";

var Context = require('web.Context');
var ControlPanelMixin = require('web.ControlPanelMixin');
var Class = require('web.Class');
var concurrency = require('web.concurrency');
var mixins = require('web.mixins');
var session = require('web.session');
var translation = require('web.translation');
var pyeval = require('web.pyeval');

 
var _t = translation._t;
    var DataSet = require('web.data');
            
        DataSet.include({
             
             exec_workflow: function (id, signal) {
            return this._model.exec_workflow(id, signal);
        },
    
    });
    
//      var Model = require('web.data');
//             
//         Model.include({ 
//             /**
//              * Executes a signal on the designated workflow, on the bound OpenERP model
//              *
//              * @param {Number} id workflow identifier
//              * @param {String} signal signal to trigger on the workflow
//              */
//             exec_workflow: function (id, signal) {
//                 alert(this.name);
//                 alert(signal);
//                 return session.rpc('/web/dataset/exec_workflow', {
//                     model: this.name,
//                     id: id,
//                     signal: signal
//                    
//                 });
//             },
//         
//     
//     }); 

}); 
      

odoo.define('vneuron_workflow_odoo.workflow', function (require) {
    "use strict";

    var Context = require('web.Context');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var data = require('web.data');
var data_manager = require('web.data_manager');
var dom = require('web.dom');
var pyeval = require('web.pyeval');
var SearchView = require('web.SearchView');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var session = require('web.session');
var QWeb = core.qweb;
var _t = core._t;
    var ViewManager = require('web.ViewManager');
            
    ViewManager.include({
        exec_workflow: function (id, signal,model) {
                return session.rpc('/web/dataset/exec_workflow', {
                    model: model,
                    id: id,
                    signal: signal
                   
                });
        },
        
        do_execute_action: function (action_data, env, on_closed) {
            var self = this;
            var result_handler = on_closed || function () {};
            var context = new Context(env.context, action_data.context || {});
            // OR NULL hereunder: pyeval waits specifically for a null value, different from undefined
            var recordID = env.currentID || null;
    
            // response handler
            var handler = function (action) {
                // show effect if button have effect attribute
                // Rainbowman can be displayed from two places : from attribute on a button, or from python.
                // Code below handles the first case i.e 'effect' attribute on button.
                var effect = false;
                if (action_data.effect) {
                    effect = pyeval.py_eval(action_data.effect);
                };
    
                if (action && action.constructor === Object) {
                    // filter out context keys that are specific to the current action.
                    // Wrong default_* and search_default_* values will no give the expected result
                    // Wrong group_by values will simply fail and forbid rendering of the destination view
                    var ncontext = new Context(
                        _.object(_.reject(_.pairs(self.env.context), function(pair) {
                          return pair[0].match('^(?:(?:default_|search_default_|show_).+|.+_view_ref|group_by|group_by_no_leaf|active_id|active_ids)$') !== null;
                        }))
                    );
                    ncontext.add(action_data.context || {});
                    ncontext.add({active_model: env.model});
                    if (recordID) {
                        ncontext.add({
                            active_id: recordID,
                            active_ids: [recordID],
                        });
                    }
                    ncontext.add(action.context || {});
                    action.context = ncontext;
                    // In case effect data is returned from python and also there is rainbow
                    // attribute on button, priority is given to button attribute
                    action.effect = effect || action.effect;
                    return self.do_action(action, {
                        on_close: result_handler,
                    });
                } else {
                    // If action doesn't return anything, but have effect
                    // attribute on button, display rainbowman
                    self.do_action({"type":"ir.actions.act_window_close", 'effect': effect});
                    return result_handler();
                }
            };
    
            if (action_data.special) {
                return handler({"type":"ir.actions.act_window_close"});
            } else if (action_data.type === "object") {
                var args = recordID ? [[recordID]] : [env.resIDs];
                if (action_data.args) {
                    try {
                        // Warning: quotes and double quotes problem due to json and xml clash
                        // Maybe we should force escaping in xml or do a better parse of the args array
                        var additional_args = JSON.parse(action_data.args.replace(/'/g, '"'));
                        args = args.concat(additional_args);
                    } catch(e) {
                        console.error("Could not JSON.parse arguments", action_data.args);
                    }
                }
                args.push(context);
                var dataset = new data.DataSet(this, env.model, env.context);
                return dataset.call_button(action_data.name, args).then(handler);
            } else if (action_data.type === "action") {
                return data_manager.load_action(action_data.name, _.extend(pyeval.eval('context', context), {
                    active_model: env.model,
                    active_ids: env.resIDs,
                    active_id: recordID,
                })).then(handler);
            }else  {
                var dataseta = new data.DataSet(this, env.model, env.context);
                return this.exec_workflow(recordID, action_data.name, env.model).then(handler);
            }
        },
    });

});	
 
