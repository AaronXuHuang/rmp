const filter_env_array = [
  'dev',
  'int',
  'prf',
  'qa',
  'pie',
  'stg',
  'prod']
const filter_name_array = [
  'environment', 
  'colorstack',
  'instance state',
  'partner',
  'tier']
const environment_array = [
  'env_dev', 
  'env_int', 
  'env_prf', 
  'env_qa', 
  'env_pie', 
  'env_stg', 
  'env_prod']
const colorstack_array = [
  'color_blue', 
  'color_green']
const instancestate_array = [
  'state_pending', 
  'state_running', 
  'state_shutting-down', 
  'state_terminated', 
  'state_stopping', 
  'state_stopped']
partner_array = []
tier_array = []
blueprogressbar = '<div class="progress"><div class="progress-bar progress-bar-indeterminate bg-blue"></div></div>'
window.onload = function () {
  initdatafromdb()
  }
function initdatafromdb() {
  newlabels = ""
  $('#title_filter').html(blueprogressbar)
  $.ajax({
    url: '/aws/instance/initdata/',
    type: 'GET',
    data: {
      orgunit: 'gbos'
    },
    dataType: 'JSON',
    success: function(res) {
      newlabels = ""
      for (let i = 0; i < res['partners'].length; i++) {
        partner = res['partners'][i]['name']
        newlabels += "<label class=\"form-check form-check-inline\">\
          <input id=\"partner_" + partner + "\" \
          class=\"form-check-input\" type=\"checkbox\" checked=\"\" \
          onclick=\"checkstatus('partner')\">\
          <span class=\"form-check-label\" style='width:50px'>" + partner + '</span></label>'
        partner_array.push("partner_" + partner)
      }
      newlabels += "<hr style='margin-top:1px;margin-bottom:1px'>"
      $('#collapse-partners').html(newlabels)
      newlabels = ""
      for (let i = 0; i < res['tiers'].length; i++) {
        tier = res['tiers'][i]['name']
        if ( i != res['tiers'].length - 1) {
          tier_next = res['tiers'][i+1]['name']
          start_letter_cur = tier[0]
          start_letter_next = tier_next[0]
        }
        newlabels += "<label class=\"form-check form-check-inline\">\
          <input id=\"tier_" + tier + "\" \
          class=\"form-check-input\" type=\"checkbox\" checked=\"\" \
          onclick=\"checkstatus('tier')\">\
          <span class=\"form-check-label\" style='width:50px'>" + tier + '</span></label>'
        tier_array.push("tier_" + tier)
        if (start_letter_cur != start_letter_next) {
          newlabels += "<div></div>"
        }
      }
      newlabels += "<hr style='margin-top:1px;margin-bottom:1px'>"
      $('#collapse-tiers').html(newlabels)
      $('#title_filter').html('Filter')
    }
  })
}

function fetchinstance() {
  id_all_array = [
    environment_array, 
    colorstack_array,
    instancestate_array,
    partner_array,
    tier_array
    ]
  checked_array = [
    environments = "",
    colorstacks = "",
    instance_states = "",
    partners = "",
    tiers = "",
    ip_addresses = ""
    ]
  for (let item = 0; item < id_all_array.length; item++) {
    for (let i = 0; i < id_all_array[item].length; i++) {
      if (document.getElementById(id_all_array[item][i]).checked == 1) {
        index = id_all_array[item][i].indexOf('_')
        value = id_all_array[item][i].substring(index + 1)
        if (checked_array[item] == "") {
          checked_array[item] = value
        }
        else {
          checked_array[item] += ',' + value
        }
      }
    }
  }
  for (let i = 0; i < filter_name_array.length; i++){
    if (checked_array[i].length == 0) {
      alert('No ' + filter_name_array[i] + ' selected.')
      return
    }
  }
  checked_array[5] = document.getElementById("ipaddress").value
  //console.log(checked_array[5])
  
  $('#tbody-instance').html('<tr><td></td></tr>')
  $('#title_details').html(blueprogressbar)
  $.ajax({
    url: '/aws/instance/filter/',
    type: 'GET',
    data: {
      environments: checked_array[0],
      colorstacks: checked_array[1],
      instance_states: checked_array[2],
      partners: checked_array[3],
      tiers: checked_array[4],
      ip_addresses: checked_array[5]
    },
    dataType: 'JSON',
    success: function(res) {
      newtr = ''
      $.each(res,function(env,values){
        for (let i = 0; i< values.length; i++) {
          if (values[i]['Colorstack'] == 'blue') {
            bg_icon = "<span class='status-dot bg-blue'></span> "
          }
          else {
            bg_icon = "<span class='status-dot bg-green'></span> "
          }
          if (values[i]['State'] == 'running') {
            state_icon = "<span class='badge bg-success me-1'></span> "
          }
          else {
            state_icon = "<span class='badge bg-warning me-1'></span> "
          }
          
          newtr += "<tr>"
          newtr += "<td class='sort-host'>" + values[i]['HostName'] + "</td>"
          newtr += "<td class='sort-name'>" + values[i]['Name'] + "</td>"
          newtr += "<td class='sort-tier'>" + values[i]['Tier'].toLowerCase() + "</td>"
          newtr += "<td class='sort-env'>" + values[i]['Environment'].toLowerCase() + "</td>"
          newtr += "<td class='sort-bg'>" + bg_icon + values[i]['Colorstack'] + "</td>"
          newtr += "<td class='sort-partner'>" + values[i]['Partner'].toLowerCase() + "</td>"
          newtr += "<td class='sort-state'>" + state_icon + values[i]['State'] + "</td>"
          newtr += "<td class='sort-ip'>" + values[i]['PrivateIpAddress'] + "</td>"
          newtr += "<td class='sort-id'>" + values[i]['InstanceId'] + "</td>"
          newtr += "<td class='sort-time'>" + values[i]['LaunchTime'] + "</td>"
          newtr += "</tr>"
        }
      })
      $('#tbody-instance').html(newtr)
      $('#title_details').html('Details')
      const sort_list = new List('table-default', {
        sortClass: 'table-sort',
        listClass: 'table-tbody',
        valueNames: [ 'sort-host', 'sort-name', 'sort-tier', 
          'sort-env', 'sort-bg', 'sort-partner', 'sort-state', 
          'sort-ip', 'sort-id', 'sort-time']
      });
    }
  })
}

function selectall(type) {
    switch (type) {
        case 'env':
        value = document.getElementById('env_all').checked
        for (let i = 0; i < environment_array.length; i++) {
            document.getElementById(environment_array[i]).checked = value
        }
        break
        case 'color':
        value = document.getElementById('color_all').checked
        for (let i = 0; i < colorstack_array.length; i++) {
            document.getElementById(colorstack_array[i]).checked = value
        }
        break
        case 'state':
        value = document.getElementById('state_all').checked
        for (let i = 0; i < instancestate_array.length; i++) {
            document.getElementById(instancestate_array[i]).checked = value
        }
        break
        case 'partner':
        value = document.getElementById('partner_all').checked
        for (let i = 0; i < partner_array.length; i++) {
            document.getElementById(partner_array[i]).checked = value
        }
        break
        case 'tier':
        value = document.getElementById('tier_all').checked
        for (let i = 0; i < tier_array.length; i++) {
            document.getElementById(tier_array[i]).checked = value
        }
        break
    }
}
function resetfilter() {
    id_all_array = [
    environment_array, 
    colorstack_array,
    instancestate_array,
    partner_array,
    tier_array
    ]
    for (let i = 0; i < environment_array.length; i++) {
        document.getElementById(environment_array[i]).checked = 0
    }
    for (let i = 0; i < colorstack_array.length; i++) {
        document.getElementById(colorstack_array[i]).checked = 1
    }
    for (let i = 0; i < instancestate_array.length; i++) {
        document.getElementById(instancestate_array[i]).checked = 0
    }
    for (let i = 0; i < partner_array.length; i++) {
        document.getElementById(partner_array[i]).checked = 1
    }
    for (let i = 0; i < tier_array.length; i++) {
        document.getElementById(tier_array[i]).checked = 1
    }
    document.getElementById('env_all').checked = 0
    document.getElementById('color_all').checked = 1
    document.getElementById('state_all').checked = 0
    document.getElementById('partner_all').checked = 1
    document.getElementById('tier_all').checked = 1
    document.getElementById('state_running').checked = 1
}

function checkstatus(type) {
    switch (type) {
        case 'env':
        document.getElementById('env_all').checked = 1
        for (let i = 0; i < environment_array.length; i++) {
            if (document.getElementById(environment_array[i]).checked == 0) {
                document.getElementById('env_all').checked = 0
                break
            }
        }
        break
        case 'color':
        document.getElementById('color_all').checked = 1
        for (let i = 0; i < colorstack_array.length; i++) {
            if (document.getElementById(colorstack_array[i]).checked == 0 ) {
                document.getElementById('color_all').checked = 0
                break
            }
        }
        break
        case 'state':
        document.getElementById('state_all').checked = 1
        for (let i = 0; i < instancestate_array.length; i++) {
            if (document.getElementById(instancestate_array[i]).checked == 0 ) {
                document.getElementById('state_all').checked = 0
                break
            }
        }
        break
        case 'partner':
        document.getElementById('partner_all').checked = 1
        for (let i = 0; i < partner_array.length; i++) {
            if (document.getElementById(partner_array[i]).checked == 0 ) {
                document.getElementById('partner_all').checked = 0
                break
            }
        }
        break
        case 'tier':
        document.getElementById('tier_all').checked = 1
        for (let i = 0; i < tier_array.length; i++) {
            if (document.getElementById(tier_array[i]).checked == 0) {
                document.getElementById('tier_all').checked = 0
                break
            }
        }
        break
    }
}

function setborder(type) {
  accordion_all = ['env', 'color', 'state', 'partner', 'tier', 'ip']
  accordion_name = ("accordion-" + type)
  
  style = document.getElementById(accordion_name).getAttribute("style")
  if (style.length == 0) {
    document.getElementById(accordion_name).setAttribute("style", "border-color: #bbdefb;border-width: 3px;border-top-style: solid")
  }
  else {
    document.getElementById(accordion_name).setAttribute("style", "")
  }
  for (let i in accordion_all) {
    if (accordion_all[i] != type) {
      document.getElementById("accordion-" + accordion_all[i]).setAttribute("style", "")
    }
  }
}