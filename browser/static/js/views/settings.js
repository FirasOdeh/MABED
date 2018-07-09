app.views.settings = Backbone.View.extend({
    template: _.template($("#tpl-page-settings").html()),
    events: {
        'submit #settings_form': 'create_session',
        'submit #session_form': 'switchSession',
        'click #deleteSession': 'deleteSession'
    },
    initialize: function() {
        this.render();
        var handler = _.bind(this.render, this);
    },
    render: function(){
        var html = this.template();
        this.$el.html(html);
        this.delegateEvents();
        this.all_sessions();
        this.show_seesion_info();

        return this;
    },
    create_session: function(e){
      e.preventDefault();
      var self = this;
      $.post('http://localhost:2016/add_session', $('#settings_form').serialize(), function(response){
          console.log( response );
          self.all_sessions();
          self.all_sessions();
      }, 'json');
      return false;
    },
    switchSession: function(e){
      e.preventDefault();
      var self = this;
      var id = $( "#sessionsList option:selected").attr('value');
      $.post('http://localhost:2016/get_session',  $('#session_form').serialize(), function(response){
          if(response.result==true){
            app.session_id = response.body._id;
            app.session = response.body._source;
            self.show_seesion_info();
            localStorage.removeItem('session_id');
            localStorage.removeItem('session');
            localStorage.setItem('session_id', response.body._id);
            localStorage.setItem('session', JSON.stringify(response.body._source));
            console.log("sesssss");
            console.log(response);
            if(response.body._source.events){
              var collection = JSON.parse(response.body._source.events);
              console.log(collection);
              app.eventsCollection.add_json_events(collection);
            }else{
              app.eventsCollection.reset();
              localStorage.removeItem('events');
            }
          }
      }, 'json');
      return false;
    },
    show_seesion_info: function(){
        if(app.session){
          $('#cs_name').html(app.session.s_name);
          $('#cs_index').html(app.session.s_index);
          $('#cs_type').html(app.session.s_type);
          $('#cs_id').html(app.session_id);
        }else{
          this.all_sessions();
        }
    },
    all_sessions: function(){
      var self = this;
      $.get('http://localhost:2016/sessions', null, function(response){
          var html = "";
          $.each(response, function(i, s){
            if(i==0&&app.session_id==null){
              app.session_id = s._id;
              app.session = s._source;
              self.show_seesion_info();
              localStorage.removeItem('session_id');
              localStorage.removeItem('session');
              localStorage.setItem('session_id', s._id);
              localStorage.setItem('session', JSON.stringify(s._source));
            }
            if(s._id==app.session_id){
                html+= '<option selected value="'+s._id+'">'+s._source.s_name+'</option>';
            }else{
                html+= '<option value="'+s._id+'">'+s._source.s_name+'</option>';
            }
          });
          $('#sessionsList').html(html);
          self.show_seesion_info();
      }, 'json');
    },
    deleteSession: function(e){
      e.preventDefault();
      var self = this;
      $.post('http://localhost:2016/delete_session', {id: app.session_id}, function(response){
          console.log( response );
          self.all_sessions();
          self.all_sessions();
          app.session_id = null;
          app.session = null;
          self.show_seesion_info();
      }, 'json');
      return false;
    }
});