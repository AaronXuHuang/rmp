document.addEventListener("DOMContentLoaded", function() {
const list = new List('table-default', {
  sortClass: 'table-sort',
  listClass: 'table-tbody',
  valueNames: [ 'sort-name', 'sort-server', 'sort-environment', 'sort-project' ]
});
})
var setInterval_ID = ""
var pool_name_auto = ""
var server_name_auto = ""
var pool_changed = 0
var max_refresh_count = 60
var refresh_count = 0
var interval = 30000
blueprogressbar = '<div class="progress"><div class="progress-bar progress-bar-indeterminate bg-blue"></div></div>'
function getpoolstate(server_name, pool_name) {
  currentTime = moment().format('HH:mm:ss');
  $.ajax({
    url: '/f5/pool/state/',
    type: 'GET',
    data: {
      server_name: server_name,
      pool_name: pool_name
    },
    dataType: 'JSON',
    success: function(res) {
      $('#getstate').html("Pool state table updated at " + currentTime);
      $('#' + server_name + '_' + pool_name + '_connection').html(res.connection);
      $('#' + server_name + '_' + pool_name + '_time').html(currentTime);
      if (res.state == 'available') {
        $('#' + server_name + '_' + pool_name + '_state').html('<span class="badge bg-success me-1"></span> Running ');
      }
      else {
        $('#' + server_name + '_' + pool_name + '_state').html('<span class="badge bg-danger me-1"></span> Stopped ');
      }
    },
    error: function(res) {
      $('#getstate').html("Pool state table updated at " + currentTime);
      $('#' + server_name + '_' + pool_name + '_connection').html('Error');
      $('#' + server_name + '_' + pool_name + '_time').html(currentTime);
      $('#' + server_name + '_' + pool_name + '_state').html('<span class="badge bg-danger me-1"></span> Error ');
    }
  })
}
function removepool(server_name, pool_name) {
  const itmes = ["_name", "_server", "_project", "_environment", "_state", "_connection", "_time"];
  for (let i = 0; i < itmes.length; i++) {
    $('#' + server_name + '_' + pool_name + itmes[i]).html(blueprogressbar);
  }
  $.ajax({
    url: '/f5/pool/remove/',
    type: 'GET',
    data: {
      server_name: server_name,
      pool_name: pool_name
    },
    dataType: 'JSON',
    success: function() {
      $('#' + server_name + '_' + pool_name + '_tr').remove();
    }
  })
}
function getmember(server_name, pool_name) {
  pool_trs = document.getElementsByClassName("pool-tr")
  for (let i = 0; i < pool_trs.length; i++) {
    document.getElementById(pool_trs[i].id).style.borderColor=""
    document.getElementById(pool_trs[i].id).style.borderWidth="" 
  }
  document.getElementById(server_name + '_' + pool_name + '_tr').style.borderColor="#bbdefb"
  document.getElementById(server_name + '_' + pool_name + '_tr').style.borderWidth="3px"
  getpoolstate(server_name, pool_name)
  currentTime = moment().format('HH:mm:ss');
  members = ""
  state = ""
  $('#poolname').removeAttr('style')
  $('#poolname').html(blueprogressbar);
  $('#membertable').html(members);
  server_name_auto = server_name
  pool_name_auto = pool_name
  if (setInterval_ID != ""){
    clearInterval(setInterval_ID)
    setInterval_ID = ""
    pool_changed = 1
  }
  else{
    pool_changed = 0
  }
  $.ajax({
    url: '/f5/member/state/',
    type: 'GET',
    data: {
      server_name: server_name,
      pool_name: pool_name
    },
    dataType: 'JSON',
    success: function(res) {
      for (let i = 0; i < res.length; i++) {
        if (res[i].state == 'available') {
          state = '<span class="badge bg-success me-1"></span> Running '
        }
        else {
          state = '<span class="badge bg-danger me-1"></span> Stopped '
        }
        members += '<tr>\
          <td>' + res[i].name + '</td>\
          <td id=memberstate_' + i + '>' + state + '</td>\
          <td id=membercurconn_' + i + '>' + res[i].curconn + '</td>\
          <td id=membermaxconn_' + i + '>' + res[i].maxconn + '</td>\
          <td id=membertotalconn_' + i + '>' + res[i].totconn + '</td></tr>'
      }
      $('#poolname').html(pool_name + ' updated at ' + currentTime);
      $('#membertable').html(members);
      pool_changed = 0
      autorefresh()
    },
    error: function(res) {
      $('#poolname').attr("style", "color:red;")
      $('#poolname').html('Get member error');
    }
  })
}
function autorefresh(){
  status = document.getElementById("autorefresh").checked
  if (status == "true") {
    refresh_count = 0
    setInterval_ID = setInterval(updatestate, interval, server_name_auto, pool_name_auto);
  }
  else{
    clearInterval(setInterval_ID)
    setInterval_ID = ""
  }
}
function updatestate(server_name, pool_name) {
  if (refresh_count == max_refresh_count) {
    clearInterval(setInterval_ID)
    document.getElementById("autorefresh").checked = 0
    return true
  }
  if (pool_changed == 1) {
    return true
  }
  currentTime = moment().format('HH:mm:ss');
  refresh_count ++
  $.ajax({
    url: '/f5/member/state/',
    type: 'GET',
    data: {
      server_name: server_name,
      pool_name: pool_name
    },
    dataType: 'JSON',
    success: function(res) {
      for (let i = 0; i < res.length; i++) {
        getpoolstate(server_name, pool_name)
        if (res[i].state == 'available') {
          state = '<span class="badge bg-success me-1"></span> Running '
        }
        else {
          state = '<span class="badge bg-danger me-1"></span> Stopped '
        }
        $('#memberstate_' + i).html(state)
        $('#membercurconn_' + i).html(res[i].curconn)
        $('#membermaxconn_' + i).html(res[i].maxconn)
        $('#membertotalconn_' + i).html(res[i].totconn)
      }
      $('#poolname').html(pool_name + ' updated at ' + currentTime);
    },
    error: function(res) {
      $('#poolname').attr("style", "color:red;")
      $('#poolname').html('get member error');
    }
  })
}
function poolaction(server_name, pool_name, action) {
  const itmes = ["_state", "_connection", "_time"];
  for (let i = 0; i < itmes.length; i++) {
    $('#' + server_name + '_' + pool_name + itmes[i]).html(blueprogressbar);
  }
  $('#poolname').html(blueprogressbar);
  $.ajax({
    url: '/f5/pool/action/',
    type: 'GET',
    data: {
      server_name: server_name,
      pool_name: pool_name,
      action: action
    },
    dataType: 'JSON',
    success: function(res) {
      updatestate(server_name, pool_name)
    },
    error: function(res) {
      updatestate(server_name, pool_name)
    }
  })
}
function confirmaction(message, func_name, server_name, pool_name, action) {
  confirmed = confirm(message)
  if (confirmed == true) {
    switch (func_name) {
      case 'getmember':
        getmember(server_name, pool_name)
        break
      case 'poolaction':
        poolaction(server_name, pool_name, action)
        break
      case 'removepool':
        removepool(server_name, pool_name)
        break
      default:
        alert("Error command")
    }
  }
}