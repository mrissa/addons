odoo.define('std.etablissement', function (require) {
    "use strict";

    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var WebClient = require('web.WebClient');
            
    WebClient.include({
        init: function(parent, client_options) {
            this._super(parent, client_options);
            this.set('title_part', {"zopenerp": "SIGE"});
        },
    });

});	
      