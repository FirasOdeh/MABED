app.views.mabed = Backbone.View.extend({
    template: _.template($("#tpl-page-mabed").html()),
    events: {
        'submit #run_mabed': 'run_mabed',
        'click body': 'test'
    },
    test: function(){
        alert("test");
       $.confirm({
            title: 'Export as .Zip file',
            boxWidth: '600px',
            useBootstrap: false,
            theme: 'pix-default-modal',
            backgroundDismiss: true,
            content: 'Don\'t forget to save the project before exporting it.',
            buttons: {
                cancel: {
                    text: 'CANCEL',
                    btnClass: 'btn-cancel',
                },
                publish: {
                    text: 'GO TO EXPORT PAGE',
                    btnClass: 'btn-blue',
                    keys: ['enter', 'shift'],
                    action: function(){
                        window.open('export',"_blank");
                    }
                }
            }
        });
    },
    initialize: function() {
        // this.render();
        var handler = _.bind(this.render, this);
    },
    render: function(){
        var html = this.template();
        this.$el.html(html);
        this.delegateEvents();
        // $('#mabed_result').html(this.model);
        //  var jc = $.confirm({
        //     theme: 'pix-default-modal',
        //     title: 'Saving Project',
        //     boxWidth: '600px',
        //     useBootstrap: false,
        //     backgroundDismiss: true,
        //     content: 'Please Don\'t close the page until you get the success notification.<div class=" jconfirm-box jconfirm-hilight-shake jconfirm-type-default  jconfirm-type-animated loading" role="dialog"></div>',
        //     defaultButtons: false,
        //     buttons: {
        //         cancel: {
        //             text: 'OK',
        //             btnClass: 'btn-cancel'
        //         }
        //     },
        // });
        return this;
    },
    run_mabed: function(e){
      e.preventDefault();
      // localStorage.removeItem('events');
      console.log("Running MABED...");
      $('#mabed_loading').fadeIn('slow');
      var self = this;
      var data = $('#run_mabed').serializeArray();
      data.push({name: "index", value: app.session.s_index});
      data.push({name: "session", value: app.session.s_name});
      console.log(data);
      $.post('http://localhost:2016/detect_events', data, function(response){
          console.log( response );

          $('#mabed_loading').fadeOut();
          if(response.result){
              self.model.reset();
              $.each(response.events.event_descriptions, function( i, value ) {
                self.model.add_event(value[0], value[1], value[2], value[3], value[4]);
              });
              var jsonCollection = JSON.stringify(self.model.toJSON());
              var impact_dataCollection = JSON.stringify(response.events.impact_data);
              console.log("jsonCollection");
              console.log(jsonCollection);
              localStorage.removeItem('events');
              localStorage.removeItem('impact_data');
              localStorage.setItem('events', jsonCollection);
              localStorage.setItem('impact_data', impact_dataCollection);
              $.post('http://localhost:2016/update_session_results', {index: app.session_id, events: jsonCollection, impact_data:impact_dataCollection}, function(res){
                  console.log(res);
              });
          }else{
              console.log("No result");
          }

      }, 'json');

      return false;
    }
});
