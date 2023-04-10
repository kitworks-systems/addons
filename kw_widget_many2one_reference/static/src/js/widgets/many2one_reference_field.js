odoo.define('kw_widget_many2one_reference.many2one_reference_field', function(require) {
'use strict';

var fieldRegistry = require('web.field_registry');
var relational_fields = require('web.relational_fields');
var basic_fields = require('web.basic_fields');
var FieldChar = require('web.basic_fields').FieldChar;
var dialogs = require('web.view_dialogs');
var core = require('web.core');
var _t = core._t;


var FieldMany2OneReference = relational_fields.FieldMany2One.extend({
    supportedFieldTypes: ['many2one_reference'],
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);

        // needs to be copied as it is an unmutable object
        this.field = _.extend({}, this.field);
        core.bus.on("update_reference_model", this, this.setRelationModel);
        this._setState();
    },
    setRelationModel: async function(model, isOpen=false) {
        const isValid = await this.checkModel(model);
        if (isValid && this.field.relation !== model) {
            this._setRelation(model);
            if (!isOpen) {
                this.value = 0;
                this.m2o_value = "";
            }
        } else {
            this._setRelation("");
        }
        this._render();
    },

    checkModel: async function(model) {
        if (!model) {
            return false;
        }
        const self = this;
        const data = await this._rpc({
            model: 'ir.model',
            method: 'search_read',
            domain: [['model', '=', model]],

        });
        console.log(data);
        if (data.length > 0) {        
            return true;
        }
        return false;
    },

    _getNameOfModel: async function () {
        if (!this.field.relation || !this.value) {
            return "";
        }
        var data = await this._rpc({
            model: this.field.relation,
            method: 'read',
            args: [[this.value], ['name']]
        })
        if (!!data && data.length > 0) {
            return data[0].name;
        } else {
            return "";
        }
    },

    _setRelation: function (model) {
        // used to generate the search in many2one
        this.field.relation = model;
    },
    /**
     * @private
     */
    _setState: function () {
        if (this.value && this.attrs.options.model_field) {
            this.setRelationModel(this.recordData[this.attrs.options.model_field], true);
        }
    },

    _getDisplayName: function (value) {
        return value;
    },

    _parseValue: function (value) {
        return value.id;
    },

    _renderEdit: async function () {
        
        if (!this.field.relation) {
            this.$el.hide();
            return;
        } else {
            this.$el.show();
        }
        var value = await this._getNameOfModel();
        // this is a stupid hack necessary to support the always_reload flag.
        // the field value has been reread by the basic model.  We use it to
        // display the full address of a partner, separated by \n.  This is
        // really a bad way to do it.  Now, we need to remove the extra lines
        // and hope for the best that no one tries to uses this mechanism to do
        // something else.
        if (this.nodeOptions.always_reload) {
            value = this._getDisplayName(value);
        }
        this.$input.val(value);
        if (!this.autocomplete_bound) {
            this._bindAutoComplete();
        }
        this._updateExternalButton();
    },

    _renderReadonly: async function () {
        
        if (!this.field.relation) {
            this.$el.hide();
            return;
        } else {
            this.$el.show();
        }
        this.m2o_value = await this._getNameOfModel();
        var escapedValue = _.escape((this.m2o_value || "").trim());
        var value = escapedValue.split('\n').map(function (line) {
            return '<span>' + line + '</span>';
        }).join('<br/>');
        this.$el.html(value);
        if (!this.noOpen && this.value) {
            this.$el.attr('href', _.str.sprintf('#id=%s&model=%s', this.value, this.field.relation));
            this.$el.attr('target', '_blank');
            this.$el.addClass('o_form_uri');
        }
    },

    _onExternalButtonClick: function () {
        if (!this.value) {
            this.activate();
            return;
        }
        var self = this;
        var context = this.record.getContext(this.recordParams);
        this._rpc({
                model: this.field.relation,
                method: 'get_formview_id',
                args: [[this.value]],
                context: context,
            })
            .then(function (view_id) {
                new dialogs.FormViewDialog(self, {
                    res_model: self.field.relation,
                    res_id: self.value,
                    context: context,
                    title: _t("Open: ") + self.string,
                    view_id: view_id,
                    readonly: !self.can_write,
                    on_saved: function (record, changed) {
                        if (changed) {
                            const _setValue = self._setValue.bind(self, self.value, {
                                forceChange: true,
                            });
                            self.trigger_up('reload', {
                                db_id: self.value,
                                onSuccess: _setValue,
                                onFailure: _setValue,
                            });
                        }
                    },
                }).open();
            });
    },
    _onClick: function (event) {
        var self = this;
        if (this.mode === 'readonly' && !this.noOpen) {
            event.preventDefault();
            event.stopPropagation();
            this._rpc({
                    model: this.field.relation,
                    method: 'get_formview_action',
                    args: [[this.value]],
                    context: this.record.getContext(this.recordParams),
                })
                .then(function (action) {
                    self.trigger_up('do_action', {action: action});
                });
        }
    },

});

var FieldMany2OneReferenceToModel = basic_fields.FieldChar.extend({

    init: function() {
        this._super.apply(this, arguments);

        core.bus.trigger("update_reference_model", this.value);
    },

    _setValue: function (value, options) {
        core.bus.trigger("update_reference_model", value);
        return this._super(value, options);
    },

});

fieldRegistry.add('many2one_reference', FieldMany2OneReference);
fieldRegistry.add('many2one_reference_model', FieldMany2OneReferenceToModel);

});