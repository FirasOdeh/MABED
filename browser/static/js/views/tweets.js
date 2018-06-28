app.views.tweets = Backbone.View.extend({
    template: _.template($("#tpl-page-tweets").html()),
    events: {
        'submit #tweets_form': 'tweets_submit'
    },
    initialize: function() {
        this.render();
        var handler = _.bind(this.render, this);
    },
    render: function(){
        var html = this.template();
        this.$el.html(html);
        this.delegateEvents();
        $('.popover-dismiss').popover({
          trigger: 'focus',
          html: true,
          content:  'The search query supports the following special characters:<ul>'+
                    '<li> + signifies AND operation</li>'+
                    '<li> | signifies OR operation</li>'+
                    '<li> - negates a single token</li>'+
                    '<li> " wraps a number of tokens to signify a phrase for searching</li>'+
                    '<li> * at the end of a term signifies a prefix query</li>'+
                    '<li> ( and ) signify precedence</li>'+
                    '<li> ~N after a word signifies edit distance (fuzziness)</li>'+
                    '<li> ~N after a phrase signifies slop amount</li></ul>'
        });

        return this;
    },
    tweets_submit: function(e){
      e.preventDefault();
      $('#tweets_results').fadeOut('slow');
      $('.loading_text').fadeIn('slow');
      var t0 = performance.now();
      var html = "";
      var data = $('#tweets_form').serializeArray();
      data.push({name: "index", value: app.session.s_index});
      var self = this;
      $.post('http://localhost:2016/tweets', data, function(response){
        // console.log(response);
        self.display_tweets(response, t0, data.unique_id);
        // var template = _.template($("#tpl-item-tweet").html());
          // $.each(response.tweets, function(i, tweet){
          //   var imgs = "";
          //   if('extended_entities' in tweet._source){
          //     $.each(tweet._source.extended_entities.media, function(i, media){
          //         var ext = "jpg";
          //         if(media.media_url.endsWith("png")){
          //           ext = "png";
          //         }
          //         // imgs += '<a href="'+media.media_url+'" target="_blank"><img style="margin:2px;max-height:150px;width:auto;" src="'+media.media_url+'"></a>'
          //         imgs += '<a href="http://localhost/TwitterImages/'+app.session.s_index+'/'+tweet._source.id_str+"_"+i+'.'+ext+'" target="_blank"><img style="margin:2px;max-height:150px;width:auto;" src="http://localhost/TwitterImages/'+app.session.s_index+'/'+tweet._source.id_str+"_"+i+'.'+ext+'"></a>'
          //     });
          //   }
          //   // var text = tweet._source.text.replace(new RegExp("hi", "ig"), '<span class="word_highlight">hi</span>');
          //   html += template({
          //                     name: tweet._source.user.name,
          //                     screen_name: tweet._source.user.screen_name,
          //                     created_at: tweet._source.created_at,
          //                     link: tweet._source.link,
          //                     text:  tweet._source.text,
          //                   classes: 'tweet_box',
          //                     images: imgs
          //                   });
          // });
          // var html = this.get_tweets_html(response, '');
          // var chtml = "";
          // $.each(response.clusters, function(i, cluster){
          //     var cbg = "";
			// 			if(cluster.size>cluster.doc_count){
			// 				cbg = 'yellow-tweet';
			// 			}
          //   chtml += '<div class="card p-3 '+cbg+'">'+
          //     '<img class="card-img-top" src="http://localhost/TwitterImages/'+app.session.s_index+'/'+cluster.image+'" alt="">'+
          //     '<div class="card-body">'+
          //     '<p class="card-text">'+cluster.doc_count+' related tweets contain this image</p>'+
          //     '<p class="card-text">Cluster size: '+cluster.size+'</p>'+
          //     '<p class="card-text">Cluster ID: '+cluster.key+'</p>'+
          //     '</div>'+
          //   '</div>';
          // });


      }, 'json');

      return false;
    },
    get_tweets_html: function(response, classes, cid){
        var html = "";
        var template = _.template($("#tpl-item-tweet").html());
        $.each(response.tweets, function(i, tweet){
            var imgs = "";
            var t_classes = classes;
            if('extended_entities' in tweet._source){
              $.each(tweet._source.extended_entities.media, function(i, media){
                    var ext = "jpg";
                    if(media.media_url.endsWith("png")){
                        ext = "png";
                    }
                        imgs += '<a href="http://localhost/TwitterImages/'+app.session.s_index+'/'+tweet._source.id_str+"_"+i+'.'+ext+'" target="_blank"><img style="margin:2px;max-height:150px;width:auto;" src="http://localhost/TwitterImages/'+app.session.s_index+'/'+tweet._source.id_str+"_"+i+'.'+ext+'"></a>'
              });
            }
            html += template({
                          name: tweet._source.user.name,
                          screen_name: tweet._source.user.screen_name,
                          created_at: tweet._source.created_at,
                          link: tweet._source.link,
                          text:  tweet._source.text,
                          classes: t_classes,
                          images: imgs
                        });
        });
        return html;
    },
    display_tweets: function(response, t0, eid){
        var html = this.get_tweets_html(response, '');
        var chtml = "";
        var i = 0;
        $.each(response.clusters, function(i, cluster){
            if(i>=20){return false;}
            i++;
            var cbg = "";
            if(parseInt(cluster.size)>parseInt(cluster.doc_count)){
                cbg = 'yellow-tweet';
            }
            chtml += '<div class="card p-3 '+cbg+'">'+
                '<img class="card-img-top" src="http://localhost/TwitterImages/'+app.session.s_index+'/'+cluster.image+'" alt="">'+
                '<div class="card-body">'+
                    '<p class="card-text">'+cluster.doc_count+' related tweets contain this image</p>'+
                    '<p class="card-text">'+cluster.size2+' related tweets contain this image</p>'+
                    '<p class="card-text">Cluster size: '+cluster.size+'</p>'+
                    '<p class="card-text">Cluster ID: '+cluster.key+'</p>'+
                '</div>'+
            '</div>';
        });
        $('#tweets_result').html(html);
        $('#imagesClusters').html(chtml);
        $('.loading_text').fadeOut('slow');
        $('#tweets_results').fadeIn('slow');
        var t1 = performance.now();
        var time = (t1 - t0) / 1000;
        var roundedString = time.toFixed(2);
        $('#res_num').html(response.tweets.length);
        $('#res_time').html(roundedString);

    }
});
