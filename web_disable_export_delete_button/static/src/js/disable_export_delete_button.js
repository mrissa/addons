odoo.define("web_disable_export_delete_button", function(require) {
"use strict";

    var core = require("web.core");
    var Sidebar = require('web.Sidebar');
    var ListController = require("web.ListController");
    var _t = core._t;
    var session = require("web.session");

    ListController.include({
        
    	/**
         * Render the sidebar (the 'action' menu in the control panel, right of the
         * main buttons)
         *
         * @param {jQuery Node} $node
         */
        renderSidebar: function ($node) {
            if (this.hasSidebar && !this.sidebar) {
            	
            	var has_export_group = false;
            	this.getSession().user_has_group('web_disable_export_delete_button.group_export_button').then(function(has_group) {
                    if(has_group) {
                    	has_export_group = true;
                    } else {
                    	has_export_group = false;
                    }
                });
                
                var has_delete_group = false;
            	this.getSession().user_has_group('web_disable_export_delete_button.group_delete_button').then(function(has_group) {
                    if(has_group) {
                    	has_delete_group = true;
                    } else {
                    	has_delete_group = false;
                    }
                });
                
                if (session.is_superuser) {
					has_export_group = true;
					has_delete_group = true;
				}
                    
				var other = [];
				
				if (has_export_group) {
					other.push({
						label: _t("Export"),
						callback: this._onExportData.bind(this)
					});
				}
				
				if (this.archiveEnabled) {
					other.push({
						label: _t("Archive"),
						callback: this._onToggleArchiveState.bind(this, true)
					});
					other.push({
						label: _t("Unarchive"),
						callback: this._onToggleArchiveState.bind(this, false)
					});
				}
				
				if (this.is_action_enabled('delete')) {
					
					if (has_delete_group) {
						other.push({
							label: _t('Delete'),
							callback: this._onDeleteSelectedRecords.bind(this)
						});
					}
                }
				this.sidebar = new Sidebar(this, {
					editable: this.is_action_enabled('edit'),
					env: {
						context: this.model.get(this.handle, {raw: true}).getContext(),
						activeIds: this.getSelectedIds(),
						model: this.modelName,
					},
					actions: _.extend(this.toolbarActions, {other: other}),
				});

				this.sidebar.appendTo($node);
				this._toggleSidebar();

            }
        }
    });
});
