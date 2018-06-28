app.views.events = Backbone.View.extend({
		template: _.template($("#tpl-page-events").html()),
		events: {

		},
	  initialize: function() {
	      this.render();
	      var handler = _.bind(this.render, this);
	  },
	  render: function(){
	    var html = this.template({});
	  	this.$el.html(html);
	  	this.delegateEvents();
	  	return this;
	  }
});
