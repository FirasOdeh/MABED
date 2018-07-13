app.views.events = Backbone.View.extend({
	template: _.template($("#tpl-page-events").html()),
	events: {
		'click .export_tweets': 'export_tweets'
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
	},
	export_tweets: function(e){
		e.preventDefault();
		var win = window.open(app.appURL+'export_confirmed_tweets?session='+app.session_id, '_blank');
		return false;
	}
});
