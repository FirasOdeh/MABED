app.views.client = Backbone.View.extend({
		template: _.template($("#tpl-page-2").html()),
		events: {
				'click .event_word_btn': 'timeline_btn',
				'click #reset_impact': 'reset_impact',
				'click .tl_options_btn': 'mark_event',
				'click .cluster_tweets': 'cluster_tweets',
				'click .tweet_state': 'tweet_state'
		},
	  initialize: function() {
	      this.render();
	      var handler = _.bind(this.render, this);
	      var self = this;
	      $(document).on("click","body .tweet_state",function(e){
			self.tweet_state(e);
		});
	  },
	  render: function(){
	    var html = this.template({});
	  	this.$el.html(html);
	  	this.delegateEvents();
		this.load_timeline();
		this.load_impact();
	  	return this;
	  },
		load_timeline: function(){
			var self = this;
			console.log("Timeline");
			data = app.eventsCollection.get_timeline_events();
			if($('#timeline-embed').length){
				timeline = new TL.Timeline('timeline-embed',data,{
					timenav_height: 260,
					marker_height_min: 40
				});
				var s_ev = app.eventsCollection.get({ cid: timeline.config.events[0].unique_id }).toJSON();
				var t0 = performance.now();
				$.post('http://localhost:2016/event_tweets', {obj: JSON.stringify(s_ev), index: app.session.s_index}, function(response){
					self.display_tweets(response, t0, timeline.config.events[0].unique_id);
				}, 'json');

				timeline.on('change', function(data) {
						var ev = app.eventsCollection.get({ cid: data.unique_id }).toJSON();
						 self.load_impact(ev.main_term);
						$('#tweets_results').fadeOut('slow');
			      $('.loading_text').fadeIn('slow');
			      var t0 = performance.now();
					$.post('http://localhost:2016/event_tweets', {obj: JSON.stringify(ev), index: app.session.s_index}, function(response){
						self.display_tweets(response, t0, data.unique_id);
					}, 'json');
				});
			}
		},
		reset_impact: function(e){
			e.preventDefault();
			this.load_impact();
			return false;
		},
		load_impact: function(event){
			if($('#chartDiv').length){
					$('#chartDiv').fadeOut('slow');

					var event_impact = JSON.parse(app.session.impact_data);
					if(event){
						$.each(event_impact, function(i, e){
							if(e.key!=event){
								var opacity = (Math.floor(Math.random() * 10) + 1)*0.1;
								e.color = 'rgba(0,0,0,'+ opacity +')';
							}
						});
					}
					var chart;
					nv.addGraph(function() {
							chart = nv.models.stackedAreaChart()
									.useInteractiveGuideline(true)
									.x(function(d) { return d[0] })
									.y(function(d) { return d[1] })
									.controlLabels({stacked: "Stacked"});

							chart.yAxis.scale().domain([0, 20]);
							chart.xAxis.tickFormat(function(d) { return d3.time.format('%x')(new Date(d)) });
							chart.yAxis.tickFormat(d3.format(',.4f'));
							chart.height(300);

							chart.legend.vers('furious');

							chart.showControls(false);
							$('#chartDiv').html('<svg id="chart1" style="height: 300px;"></svg>')
							var output = d3.select('#chart1')
									.datum(event_impact)
									.call(chart);
							nv.utils.windowResize(chart.update);
							return chart;
					});
					$('#chartDiv').fadeIn('slow');
			}

		},
		timeline_btn: function(e){
			e.preventDefault();
			var self = this;
			var word = $(e.currentTarget).data("value");
			$('#tweets_results').fadeOut('slow');
			$('.loading_text').fadeIn('slow');
			var t0 = performance.now();
			$.post('http://localhost:2016/tweets', {word:word, index: app.session.s_index}, function(response){
						self.display_tweets(response, t0);
			}, 'json');

			return false;
		},
		mark_event: function(e){
			e.preventDefault();
			var self = this;
			var s_ev = JSON.stringify(app.eventsCollection.get({ cid: $(e.currentTarget).data("cid") }).toJSON());
			var data = [];
			data.push({name: "index", value: app.session.s_index});
			data.push({name: "session", value: app.session.s_name});
			data.push({name: "event", value: s_ev});
			data.push({name: "status", value: $(e.currentTarget).data("status")});

			$.post('http://localhost:2016/mark_event', data, function(response){
						console.log(response);
			}, 'json');
			return false;
		},
		cluster_tweets: function(e){
			e.preventDefault();
			var self = this;
			var cid = $(e.currentTarget).data("cid");
			var ev = app.eventsCollection.get({ cid: $(e.currentTarget).data("eid") }).toJSON();

			$.confirm({
					theme: 'pix-cluster-modal',
					title: 'Cluster'+cid+' Tweets',
					columnClass: 'col-md-12',
					useBootstrap: true,
					backgroundDismiss: false,
					// content: html,
					content: 'Loading... <div class=" jconfirm-box jconfirm-hilight-shake jconfirm-type-default  jconfirm-type-animated loading" role="dialog"></div>',
					defaultButtons: false,
					onContentReady: function () {

						var jc = this;
						$.post('http://localhost:2016/cluster_tweets', {cid: cid, index: app.session.s_index, obj: JSON.stringify(ev)}, function(response){
							var html = self.get_tweets_html(response, 'static_tweet_box', cid);
							self.delegateEvents();
							jc.setContent(html);
					}, 'json');
					},
					buttons: {
						cancel: {
							text: 'CLOSE',
							btnClass: 'btn-cancel'
						}
					}
				});
			return false;
		},
		get_tweets_html: function(response, classes, cid){
			var html = "";
			var template = _.template($("#tpl-item-tweet").html());
			$.each(response.tweets, function(i, tweet){
				var imgs = "";
				var t_classes = classes;
				if(response.event_tweets){
					var detected = false;
					$.each(response.event_tweets, function(i2, t){
						if(t._source.id_str===tweet._source.id_str){
							detected=true;
							return false;
						}
					});
					if(!detected){
						t_classes+= ' yellow-tweet';
					}
				}
				if('extended_entities' in tweet._source){
				  $.each(tweet._source.extended_entities.media, function(i, media){
									var ext = "jpg";
									if(media.media_url.endsWith("png")){
										ext = "png";
									}
										imgs += '<a href="http://localhost/TwitterImages/'+app.session.s_index+'/'+tweet._source.id_str+"_"+i+'.'+ext+'" target="_blank"><img style="margin:2px;max-height:150px;width:auto;" src="http://localhost/TwitterImages/'+app.session.s_index+'/'+tweet._source.id_str+"_"+i+'.'+ext+'"></a>'
				  });
				}
				var state = tweet._source['session_'+app.session.s_name];
				if(state === "confirmed"){
					state = '<span class="badge badge-success">'+state+'</span>';
				}else if (state === "negative"){
					state = '<span class="badge badge-danger">'+state+'</span>';
				}else{
					state = '<span class="badge badge-secondary">'+state+'</span>';
				}
            	html += template({
					tid: tweet._id,
                              name: tweet._source.user.name,
                              screen_name: tweet._source.user.screen_name,
                              created_at: tweet._source.created_at,
                              link: tweet._source.link,
                              text:  tweet._source.text,
							  classes: t_classes,
                              images: imgs,
								state: state
                            });
          	});
			return html;
		},
		display_tweets: function(response, t0, eid){
			var html = this.get_tweets_html(response, '');
			var chtml = "";
			var cbtn = "", state_btns="";
			var i = 0;
			$.each(response.clusters, function(i, cluster){
				if(i>=20){return false;}
				i++;
				var cbg = "";
				if(cluster.size>cluster.doc_count){
					cbg = 'yellow-tweet';
				}
				if(eid){
					cbtn = '<a href="#" class="btn btn-primary btn-flat cluster_tweets" data-eid="'+eid+'" data-cid="'+cluster.key+'"><strong>Show tweets</strong></a>';
					state_btns = '<div class="cluster_state_btns">';
					state_btns += '<a href="#" class="btn btn-outline-success" data-eid="'+eid+'" data-cid="'+cluster.key+'"><strong>Confirmed</strong></a>';
					state_btns += ' <a href="#" class="btn btn-outline-danger" data-eid="'+eid+'" data-cid="'+cluster.key+'"><strong>Negative</strong></a>';
					state_btns += '</div>';
				}
				chtml += '<div class="card p-3 '+cbg+'">'+
					'<img class="card-img-top" src="http://localhost/TwitterImages/'+app.session.s_index+'/'+cluster.image+'" alt="">'+
					state_btns+
					'<div class="card-body">'+
						'<p class="card-text">'+cluster.doc_count+' related tweets contain this image</p>'+
						// '<p class="card-text">'+cluster.size2+' related tweets contain this image</p>'+
						'<p class="card-text">Cluster size: '+cluster.size+'</p>'+
						'<p class="card-text">Cluster ID: '+cluster.key+'</p>'+
						cbtn+

					'</div>'+
				'</div>';
			});
			$('#eventsClusters').html(chtml);
			$('#tweets_result').html(html);
			$('.loading_text').fadeOut('slow');
			$('#tweets_results').fadeIn('slow');
			var t1 = performance.now();
			var time = (t1 - t0) / 1000;
			var roundedString = time.toFixed(2);
			$('#res_num').html(response.tweets.length);
			$('#res_time').html(roundedString);

		},
	tweet_state: function(e){
		e.preventDefault();
		var tid = $(e.currentTarget).data("tid");
		var val = $(e.currentTarget).data("val");
		var el = $(e.currentTarget).closest('.media-body').find('.t_state');
		console.log(el);
		$.post('http://localhost:2016/mark_tweet', {tid: tid, index: app.session.s_index, session: app.session.s_name, val: val}, function(response){
			console.log(response);
			var state = val;
				if(state === "confirmed"){
					state = '<span class="badge badge-success">'+state+'</span>';
				}else if (state === "negative"){
					state = '<span class="badge badge-danger">'+state+'</span>';
				}else{
					state = '<span class="badge badge-secondary">'+state+'</span>';
				}
				el.html(state);
		}, 'json');
		return false;
	}
});