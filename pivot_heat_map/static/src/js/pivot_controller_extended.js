odoo.define('pivot_heat_map.controllers', function (require) {
    "use strict";
    
    var PivotController = require('web.PivotController');
    var GraphController = require('web.GraphController');
    var GraphRenderer = require('web.GraphRenderer');
    var PivotRenderer = require('web.PivotRenderer');
    var core = require('web.core');
   var _t = core._t;
var qweb = core.qweb;
    GraphController.include({
    
        _onButtonClick: function (event) {
            var $target = $(event.target);
            this._super(event);
            var self = this;
            /* catching heat map button click and switching between modes*/
            
            if ($target.hasClass('o_heat_map_print_g')) {
                
                        
                        self.generate_pdf();
                }
        },
        generate_pdf: function() {
            function createPDF() {
             var svg = $('.o_view_manager_content').find('svg')[0];
                        svgAsPngUri(svg, {}, function(uri) {
                            var doc = new jsPDF({
                                 unit: 'px',
                                 format: 'A4',
                                 orientation: 'landscape'
                             });
                             
                            var title = $('ol.breadcrumb').find('li.active').html();
                            var now = new Date();
                            doc.text(now.toString(), 10, 10);
                            doc.setFont("helvetica");
                            doc.setFontType("bold");
                            doc.setTextColor(0,0,255);
                            doc.text(title, 20, 30);
                            
                            doc.addImage(uri, 'PNG', 0, 60, 500,300);
                            doc.save('graph2.pdf');
                            
                    });
            }

            $('body').scrollTop(0);
            createPDF();

        },
    
    });
    
    GraphRenderer.include({
    
         _renderGraph: function () {
        this.$el.empty();
          var now = new Date();
         this.$el.append(qweb.render('GraphView.date', {
                datee: now,
                
            }));
        var chart = this['_render' + _.str.capitalize(this.state.mode) + 'Chart']();
        if (chart && chart.tooltip.chartContainer) {
            this.to_remove = chart.update;
            nv.utils.onWindowResize(chart.update);
            chart.tooltip.chartContainer(this.el);
        }
    },
    
    });
    
    PivotController.include({
        init: function (parent, model, renderer, params) {
            renderer.heat_map = null;
            renderer.cells = {};
            this._super(parent, model, renderer, params);
        },
        start: function () {
            this.$el.toggleClass('o_enable_linking', this.enableLinking);
            this.$fieldSelection = this.$('.o_field_selection');
            var now = new Date();
            this.$fielddate = this.$('.sige_date');
            this.$fielddate.html(now.toString());
            core.bus.on('click', this, function () {
                this.$fieldSelection.empty();
            });
            return this._super();
        },
        
        _onButtonClick: function (event) {
            var $target = $(event.target);
            this._super(event);
            var self = this;
            /* catching heat map button click and switching between modes*/
            
            if ($target.hasClass('o_heat_map_print')) {
                
                        
                        self.generate_pdf();
                }
            
            if ($target.hasClass('o_heat_map_col')) {
                if (this.renderer.heat_map == 'col' ){
                    this.renderer.heat_map = null;
                }
                else{
                    this.renderer.cells = {};
                    this.renderer.heat_map = 'col';
                }

                this.renderer._render();
            }
            else if ($target.hasClass('o_heat_map_row')) {
                if (this.renderer.heat_map == 'row'){
                    this.renderer.heat_map = null;
                }
                else{
                    this.renderer.cells = {};
                    this.renderer.heat_map = 'row';
                }

                this.renderer._render();
            }
            else if ($target.hasClass('o_heat_map_both')) {
                if (this.renderer.heat_map == 'both'){
                    this.renderer.heat_map = null;
                }
                else{
                    this.renderer.cells = {};
                    this.renderer.heat_map = 'both';
                }

                this.renderer._render();
            }
        },
        
        generate_pdf: function() {
            var form = $('.o_view_manager_content'),
            cache_width = form.width(),
            a4 = [800, 841.89]; // for a4 size paper width and height
            // create canvas object
            function getCanvas() {
                form.width((a4[0] * 1.33333) - 80).css('max-width', '1000px');
                return html2canvas(form, {
                    imageTimeout: 2000,
                    removeContainer: true
                });
            }
            function createPDF() {
                getCanvas().then(function (canvas) {
                    var
                     img = canvas.toDataURL("image/png"),
                     doc = new jsPDF({
                         unit: 'px',
                         format: 'A4',
                         orientation: 'landscape'
                     });
                    var title = $('ol.breadcrumb').find('li.active').html();
                    doc.setFont("helvetica");
                    doc.setFontType("bold");
                    doc.setTextColor(0,0,255);
                    doc.text(title, 20, 30);
                    doc.addImage(img, 'JPEG', 15, 60);
                    doc.save('pivot.pdf');
                    form.width(cache_width);
                });
            }

            $('body').scrollTop(0);
            createPDF();

        },
    });
});
