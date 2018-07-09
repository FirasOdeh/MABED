var app = (function() {

	var api = {
		views: {},
		models: {},
    collections: {},
		content: null,
		router: null,
		session_id: null,
		session: null,
		eventsCollection: null,
		init: function() {
			this.content = $("#content");

			this.eventsCollection = new app.collections.events();

			// if (localStorage.getItem('events') !== null) {
			// 	var collectionString = localStorage.getItem('events');
			// 	var collection = JSON.parse(collectionString);
			// 	console.log(collection);
			// 	this.eventsCollection.add_json_events(collection);
			// }
			if (localStorage.getItem('session_id') !== null) {
				var sessionString = localStorage.getItem('session');
				this.session = JSON.parse(sessionString);
				this.session_id = localStorage.getItem('session_id');
				if(this.session.events){
					var collection = JSON.parse(this.session.events);
					// console.log(collection);
					this.eventsCollection.add_json_events(collection);
				}
				// $.post('http://localhost:2016/get_session_results', {index: this.session_id}, function(res){
				// 	console.log("get");
				// 		console.log(res);
				// 		if(res.result&&res.body.events){
				// 			var collection = JSON.parse(res.body.events);
				// 			console.log(collection);
				// 			this.eventsCollection.add_json_events(collection);
				// 		}
				// });
			}
			Backbone.history.start();
			return this;
		},
		changeContent: function(el) {
			this.content.empty().append(el);
			return this;
		},
		title: function(str) {
				$("#title").text(str);
				$("title").text(str + " | MABED");
				return this;
		}
	};

	var ViewsFactory = {
        home: function() {
            if(!this.homeView) {
                this.homeView = new api.views.home();
            }
            return this.homeView;
        },
				settings: function() {
            if(!this.settingsView) {
                this.settingsView = new api.views.settings();
            }
            return this.settingsView;
        },
				tweets: function() {
            if(!this.tweetsView) {
                this.tweetsView = new api.views.tweets();
            }
            return this.tweetsView;
        },
				mabed: function() {
            if(!this.mabedView) {
                this.mabedView = new api.views.mabed({
									model: api.eventsCollection
								});
            }
            return this.mabedView;
        },
		client: function() {
			if(!this.clientView) {
				this.clientView = new api.views.client({
					model: api.clientCollection
				}).on("saved, submit", function(e) {
					e.preventDefault();
					api.router.navigate("client", {trigger: false});
				});
			}
			return this.clientView;
		},
		events: function() {
			if(!this.eventsView) {
				this.eventsView = new api.views.events({
					model: api.clientCollection
				});
			}
			return this.eventsView;
		}
	};

	var Router = Backbone.Router.extend({
		routes: {
			"results": "results",
			"settings": "settings",
			"tweets": "tweets",
			"mabed": "mabed",
			"events": "events",
			"": "home"
		},
        home: function() {
            var view = ViewsFactory.home();
						$('#mabed-nav .nav-item').removeClass('active');
						$('#nav-home').addClass('active');
            api
                .title("Homepage")
                .changeContent(view.$el);
            view.render();
						$('html,body').animate({scrollTop: 0}, 300);

        },
				settings: function() {
            var view = ViewsFactory.settings();
						$('#mabed-nav .nav-item').removeClass('active');
						$('#nav-settings').addClass('active');
            api
                .title("Settings")
                .changeContent(view.$el);
            view.render();
        },
				tweets: function() {
            var view = ViewsFactory.tweets();
						$('#mabed-nav .nav-item').removeClass('active');
						$('#nav-tweets').addClass('active');
            api
                .title("Tweets")
                .changeContent(view.$el);
            view.render();
        },
				mabed: function() {
            var view = ViewsFactory.mabed();
						$('#mabed-nav .nav-item').removeClass('active');
						$('#nav-mabed').addClass('active');
            api
                .title("Run")
                .changeContent(view.$el);
            view.render();
        },
				results: function(archive) {
            var view = ViewsFactory.client();
						$('#mabed-nav .nav-item').removeClass('active');
						$('#nav-results').addClass('active');
            api
                .title("Results")
                .changeContent(view.$el);
            view.render();
						$('html,body').animate({scrollTop: 0}, 300);

        },
				events: function(archive) {
            var view = ViewsFactory.events();
						$('#mabed-nav .nav-item').removeClass('active');
						$('#nav-events').addClass('active');
            api
                .title("Events")
                .changeContent(view.$el);
            view.render();
						$('html,body').animate({scrollTop: 0}, 300);

        }
	});

	api.router = new Router();

	return api;

})();