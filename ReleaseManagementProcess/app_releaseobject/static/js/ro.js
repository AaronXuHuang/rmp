env = "PIE";
state_timeId = "";
running_id = "";
bux_test = {
  PIE: "",
  STG: "",
  PROD: "",
};
bux_deployment_env = ["PIE", "STG", "PROD"];
bux_deployment_sub_env = ["PIE", "STG2", "STG1", "DC2", "DC1"];
window.onload = function () {
  $("#modal-info").modal({ backdrop: false, keyboard: false });
  $("#modal-success").modal({ backdrop: false, keyboard: false });
  $("#modal-error").modal({ backdrop: false, keyboard: false });
  $("#modal-create").modal({ backdrop: false, keyboard: false });
  $("#modal-load-bar").modal({ backdrop: false, keyboard: false });
  alert('asdf')
};
function read_jira_fix_version() {
  project = $("#jira_project").val();
  released = document.getElementById("jira_released_only").checked;
  $.ajax({
    url: "/jira/fixversion/get/",
    type: "GET",
    data: {
      project: project,
      released: !released,
    },
    dataType: "JSON",
    success: function (res) {
      var jira_fix_version =
        '<option disabled selected style="display:none"></option>';
      var fix_versions = res["fix_versions"];
      if (fix_versions.length > 0) {
        $("#jira_fix_version").prop("disabled", false);
      } else {
        $("#jira_fix_version").prop("disabled", true);
      }
      for (let i = 0; i < fix_versions.length; i++) {
        var fix_version_name = fix_versions[i].name;
        jira_fix_version +=
          '<option value="' +
          fix_version_name +
          '">' +
          fix_version_name +
          "</option>";
      }
      $("#jira_fix_version").html(jira_fix_version);
    },
  });
}
function read_rmp_fix_version() {
  orgunit = $("#rmp_orgunit").val();
  $.ajax({
    url: "/releaseobject/fixversion/get/",
    type: "GET",
    data: {
      orgunit: orgunit,
    },
    dataType: "JSON",
    success: function (res) {
      var rmp_fix_version =
        '<option disabled selected style="display:none"></option>';
      var fix_versions = res["fix_versions"];
      if (fix_versions.length > 0) {
        $("#rmp_fix_version").prop("disabled", false);
      } else {
        $("#rmp_fix_version").prop("disabled", true);
      }
      for (let i = 0; i < fix_versions.length; i++) {
        var fix_version_name = fix_versions[i];
        rmp_fix_version +=
          '<option value="' +
          fix_version_name +
          '">' +
          fix_version_name +
          "</option>";
      }
      $("#rmp_fix_version").html(rmp_fix_version);
    },
  });
}
function create_ro() {
  $("#load-ro-button").attr("disabled", true);
  $("#create-ro-button").attr("disabled", true);
  $("#load-close").attr("disabled", true);
  jira_project = $("#jira_project").val();
  jira_fix_version = $("#jira_fix_version").val();
  if (jira_project == null || jira_fix_version == null) {
    $("#error-title").text("Error!");
    $("#error-text").html(
      "<strong>Orgunit</strong> or <strong>fix version</strong> is empty!"
    );
    $("#modal-create").modal("hide");
    $("#modal-error").modal("show");
    $("#load-ro-button").attr("disabled", false);
    $("#create-ro-button").attr("disabled", false);
    return;
  }
  var ro_name = jira_project + "-" + jira_fix_version;
  $("#ro-table").html("");
  $("#modal-create").modal("hide");
  $("#modal-load-bar").modal("show");
  $("#detail-table").css({ display: "none" });
  $("#ro-process-title").css({ display: "none" });
  $("#ro-process-flow").css({ display: "none" });
  update_progress_bar(
    "running",
    "Creating RMP Release Object <strong>" + ro_name + "</strong>"
  );
  $.ajax({
    url: "/releaseobject/create/",
    type: "GET",
    data: {
      orgunit: jira_project,
      fixversion: jira_fix_version,
    },
    dataType: "JSON",
    success: function (res) {
      update_progress_bar(
        "done",
        "RMP Release Object <strong>" +
          ro_name +
          "</strong> has been created"
      );
      $("#load-ro-button").attr("disabled", false);
      $("#create-ro-button").attr("disabled", false);
      $("#load-close").attr("disabled", false);
      $("#rmp_orgunit ").get(0).selectedIndex = 0;
      $("#rmp_fix_version ").get(0).selectedIndex = 0;
      $("#rmp_fix_version ").attr("disabled", true);
    },
  });
}
function load_ro(orgunit, fix_version) {
  load_rp_table()
  alert('asdf')
  $("#load-ro-button").attr("disabled", true);
  $("#create-ro-button").attr("disabled", true);
  $("#load-close").attr("disabled", true);
  if (typeof orgunit == "undefined" || typeof fix_version == "undefined") {
    orgunit = $("#rmp_orgunit").val();
    fix_version = $("#rmp_fix_version").val();
  }
  if (orgunit == null || fix_version == null) {
    $("#error-title").text("Error!");
    $("#error-text").html(
      "<strong>Orgunit</strong> or <strong>fix version</strong> is empty!"
    );
    $("#modal-load-bar").modal("hide");
    $("#modal-error").modal("show");
    $("#load-ro-button").attr("disabled", false);
    $("#create-ro-button").attr("disabled", false);
    $("#load-close").attr("disabled", false);
    return;
  }
  var ro_name = orgunit + "-" + fix_version;
  var details_text = ro_name + " Details";
  var release_process = ro_name + " Release Process";
  $("#ro-table").html("");
  $("#modal-load-bar").modal("show");
  $("#detail-table").css({ display: "none" });
  $("#ro-process-title").css({ display: "none" });
  $("#ro-process-flow").css({ display: "none" });
  update_progress_bar(
    "running",
    "Loading RMP Release Object <strong>" + ro_name + "</strong>"
  );
  $.ajax({
    url: "/releaseobject/get/",
    type: "GET",
    data: {
      orgunit: orgunit,
      fixversion: fix_version,
    },
    dataType: "JSON",
    success: function (res) {
      create_ro_table(res);
      save_rp_components(res);
      update_offcanvas_deploy_details_component(res);
      update_progress_bar(
        "done",
        "RMP Release Object <strong>" +
          ro_name +
          "</strong> has been loaded"
      );
      show_release_process_table(orgunit);
      $("#title_details").text(details_text);
      $("#title_release_process").text(release_process);
      $("#start-release").attr("disabled", false);
      $("#detail-table").css({ display: "block" });
      $("#ro-process-title").css({ display: "block" });
      $("#ro-process-flow").css({ display: "block" });
      $("#load-ro-button").attr("disabled", false);
      $("#create-ro-button").attr("disabled", false);
      $("#load-close").attr("disabled", false);
      get_release_process_state_all();
    },
  });
}
function load_rp_table() {
  console.log('bbb')
  $('#ro-process-flow').load('release_process_bux.html')
  console.log('aaa')
}
function create_ro_table(ro) {
  fix_version = ro["information"]["fixversion"];
  orgunit = ro["information"]["orgunit"];
  octo_space = ro["information"]["space"];
  for (component_name in ro[fix_version]) {
    release_version = ro[fix_version][component_name]["releaseversion"];
    assembled = ro[fix_version][component_name]["releaseassembled"];
    environments = ro[fix_version][component_name]["environments"];
    latest = ro[fix_version][component_name]["latest"];
    issues = ro[fix_version][component_name]["issues"];
    td = create_component(component_name, octo_space);
    td += create_release_version(
      component_name,
      release_version,
      octo_space
    );
    td += create_assembled(assembled);
    td += create_environments(environments);
    td += create_latest(release_version, latest);
    td += create_issues(issues);
    tr = "<tr>" + td + "</tr>";
    $("#ro-table").append(tr);
  }
}
function create_component(component_name, octo_space) {
  octo_project_name = component_name.replace("_", "-");
  td =
    '\
  <td>\
    <span class="ro-component">\
      <a href=https://octopus.nextestate.com/app#/' +
    octo_space +
    "/projects/" +
    octo_project_name +
    '/deployments style="color:white">' +
    component_name +
    "</a>\
    </span>\
  </td>";
  return td;
}
function create_release_version(
  component_name,
  release_version,
  octo_space
) {
  octo_project_name = component_name.replace("_", "-");
  td =
    '\
<td class="text-muted">\
  <a href="https://octopus.nextestate.com/app#/' +
    octo_space +
    "/projects/" +
    octo_project_name +
    "/deployments/releases/" +
    release_version +
    '" style="color:#25782b; font-size: .8em">' +
    release_version +
    "</a>\
</td>";
  return td;
}
function create_assembled(assembled) {
  assembled = assembled.replace("T", "<br>");
  td =
    '\
<td class="text-muted" style="font-size: .9em">' +
    assembled +
    "</td>";
  return td;
}
function create_environments(environments) {
  for (name in environments) {
    if (environments[name] == "Success") {
      environments[name] = 'style="background-color:#21BA45"';
    } else {
      environments[name] = "";
    }
  }
  td =
    '\
<td class="ro-env-td">\
  <label class="ro-env-label">\
    <span class="ro-env-span"' +
    environments["BUX_QA"] +
    '>BUX_QA</span>\
    <span class="ro-env-span"' +
    environments["BUX_PRF"] +
    '>BUX_PRF</span>\
  </label>\
  <label class="ro-env-label">\
    <span class="ro-env-span"' +
    environments["BUX_PIE"] +
    '>BUX_PIE</span>\
  </label>\
  <label class="ro-env-label">\
    <span class="ro-env-span"' +
    environments["BUX_STG1"] +
    '>BUX_STG1</span>\
    <span class="ro-env-span"' +
    environments["BUX_STG2"] +
    '>BUX_STG2</span>\
  </label>\
  <label class="ro-env-label">\
    <span class="ro-env-span"' +
    environments["BUX_DC1"] +
    '>BUX_DC1</span>\
    <span class="ro-env-span"' +
    environments["BUX_DC2"] +
    ">BUX_DC2</span>\
  </label>\
</td>";
  return td;
}
function create_latest(release_version, latest) {
  result = "false";
  td =
    '<td class="text-muted" style="background-color:#ffebe6; font-size: 0.72rem">' +
    result +
    "</td>";
  if (release_version == latest) {
    result = "true";
    td =
      '<td class="text-muted" style="font-size: 0.72rem">' +
      result +
      "</td>";
  }
  return td;
}
function create_issues(issues) {
  br = "<br>";
  spans = "";
  for (name in issues) {
    if ((br = "<br>")) {
      br = "";
    } else {
      br = "<br>";
    }
    if (issues[name]["issuetype"] == "Defect") {
      img = "<img src=/static/img/exclamation.png>";
    } else {
      img = "<img src=/static/img/viewavatar.svg>";
    }
    spans +=
      '\
  <span class="ro-issue-span">\
    <a href=https://pd.nextestate.com/browse/' +
      name +
      ">" +
      img +
      "  " +
      name +
      "</a>\
  </span>" +
      br;
  }
  td = '\
<td class="ro-issue-td">' + spans + "</td>";
  return td;
}
function update_progress_bar(step, progress_bar_html) {
  running_progress =
    '\
<div class="progress" style="margin-top: 10px; margin-bottom: 10px">\
  <div class="progress-bar progress-bar-indeterminate bg-blue">\
  </div>\
</div>';
  completed_progress =
    '\
<div class="progress" style="margin-top: 10px; margin-bottom: 10px">\
  <div class="progress-bar" style="width: 100%" role="progressbar">\
  </div>\
</div>';
  error_progress = "";
  if (step == "running") {
    ro_progress_bar = running_progress;
  } else if (step == "done") {
    ro_progress_bar = completed_progress;
  }
  $("#ro_progress_text").html(progress_bar_html);
  $("#ro_progress_bar").html(ro_progress_bar);
}
function update_modal_info_for_test() {
  if (orgunit == "BUX") {
    $("#modal-info-title").text(env + " testing");
    $("#modal-info-text").html(
      "<strong>" +
        env +
        "</strong> deployment is completed and in testing now.<br> Click <code>" +
        env +
        " testing</code> to update test result manaully."
    );
    $("#confirm-yes").text("Close");
    $("#confirm-yes").attr("onclick", "");
    $("#modal-info").modal("show");
  }
}
function update_modal_info_for_release() {
  if (orgunit == "BUX") {
    if (env == "PIE") {
      $("#modal-info-title").text("Ready to release");
      $("#modal-info-text").html(
        "Start <strong>BUX</strong> release process on <strong>PIE</strong>."
      );
      $("#confirm-yes").text("Yes, start on PIE");
      $("#confirm-yes").attr(
        "onclick",
        "release_process_bux('PIE', 'start')"
      );
    } else if (env == "STG") {
      $("#modal-info-title").text("Ready to release");
      $("#modal-info-text").html(
        "Start <strong>BUX</strong> release process on <strong>STG</strong>."
      );
      $("#confirm-yes").text("Yes, start on STG");
      $("#confirm-yes").attr("onclick", "release_process_bux('STG')");
    } else if (env == "PROD") {
      $("#modal-info-title").text("Ready to release");
      $("#modal-info-text").html(
        "Start <strong>BUX</strong> release process on <strong>PROD</strong>."
      );
      $("#confirm-yes").text("Yes, start on PROD");
      $("#confirm-yes").attr("onclick", "release_process_bux('PROD')");
    } else if (env == "RELEASED") {
      $("#modal-info-title").text("Ready to close");
      $("#modal-info-text").html(
        "Close <strong>BUX</strong> release, and RMP Release Object will be locked."
      );
      $("#confirm-yes").text("Yes, close release");
      $("#confirm-yes").attr("onclick", "release_process_bux('RELEASED')");
      env = "CLOSED";
    } else if (env == "CLOSED") {
      $("#modal-info-title").text("Release closed");
      $("#modal-info-text").html(
        "<strong>BUX</strong> release has been closed."
      );
      $("#confirm-yes").text("Close");
    }
  }
}
function show_release_process_table(orgunit) {
  if (orgunit == "BUX") {
    $("#accordion-bux").css({ display: "block" });
  }
}
function update_start_release_button(env) {
  console.log(env);
  if (env == "RELEASED") {
    $("#start-release").text("Release closed");
    $("#start-release").attr("disabled", false);
    return;
  }
  if (env == "PIE") {
    $("#start-release").text("Release on PIE running");
    $("#start-release").attr("disabled", true);
  } else if (env == "STG") {
    $("#start-release").text("Release on STG running");
    $("#start-release").attr("disabled", true);
  } else if (env == "PROD") {
    $("#start-release").text("Release on PROD running");
    $("#start-release").attr("disabled", true);
  }
}
function release_process_bux(env, state) {
  update_start_release_button(env);
  $.ajax({
    url: "/releaseobject/process/run/",
    type: "GET",
    dataType: "JSON",
    data: {
      orgunit: orgunit,
      fixversion: fix_version,
      env: env,
      state: state,
    },
    success: function (res) {
      // start_state_timeId runs only once to get/update status quickly
      start_state_timeId = setInterval(function () {
        get_release_process_state();
        clearInterval(start_state_timeId);
      }, 2000);
      state_timeId = setInterval(get_release_process_state, 5000);
    },
  });
}
function get_release_process_state_all() {
  $.ajax({
    url: "/releaseobject/process/get/",
    type: "GET",
    dataType: "JSON",
    data: {
      orgunit: orgunit,
      fixversion: fix_version,
    },
    success: function (res) {
      if (orgunit == "BUX") {
        for (var state_env in bux_test) {
          var state_env_steps = res[orgunit][state_env];
          update_step_buttons(state_env_steps);
          check_state_env_steps(state_env, state_env_steps);
          update_offcanvas_deploy_details_state(state_env_steps);
        }
      }
    },
  });
}
function check_state_env_steps(state_env, state_env_steps) {
  if (orgunit == "BUX") {
    for (step in state_env_steps) {
      if (state_env_steps[step]["state"] == "running") {
        env = state_env;
        console.log(state_env);
        update_start_release_button(state_env);
        if (!step.includes("-test")) {
          state_timeId = setInterval(get_release_process_state, 5000);
        }
      }
    }
    if (
      state_env_steps[state_env.toLowerCase() + "-test"]["state"] ==
      "running"
    ) {
      update_modal_info_for_test();
      update_start_release_button(state_env);
    } else if (
      state_env_steps[state_env.toLowerCase() + "-test"]["state"] == "done"
    ) {
      update_start_release_button_after_test(state_env);
    }
  }
}
function get_release_process_state() {
  $.ajax({
    url: "/releaseobject/process/get/",
    type: "GET",
    dataType: "JSON",
    data: {
      orgunit: orgunit,
      fixversion: fix_version,
    },
    success: function (res) {
      update_step_buttons(res[orgunit][env]);
      update_offcanvas_deploy_details_state(res[orgunit][env]);
      if (
        res[orgunit][env][env.toLowerCase() + "-test"]["state"] == "running"
      ) {
        clearInterval(state_timeId);
        update_modal_info_for_test();
      }
    },
  });
}
function restore_step_buttons() {}
function update_step_buttons(tracker) {
  var attr_display;
  var css_color;
  var color_blue = "#206bc4";
  var color_green = "#21BA45";
  var color_gray = "#767676";
  for (key in tracker) {
    var button_id = "#" + key;
    $(button_id).text(tracker[key]["text"]);
    if (tracker[key]["state"] == "running") {
      attr_display = false;
      css_color = color_blue;
      if ("" == running_id) {
        button_flash(button_id, "start");
      }
    } else if (tracker[key]["state"] == "done") {
      attr_display = false;
      css_color = color_green;
      if (button_id == running_id) {
        button_flash(button_id, "stop");
      }
    } else {
      attr_display = true;
      css_color = color_gray;
    }
    attr_desc = tracker[key]["title"];
    $(button_id).attr("disabled", attr_display);
    $(button_id).attr("title", attr_desc);
    $(button_id).css({
      "background-color": css_color,
      "border-color": css_color,
    });
    //data-bs-toggle="offcanvas" href="#offcanvasStart" role="button" aria-controls="offcanvasStart"
    if (!key.includes("-test")) {
      set_step_offcanvas(key, tracker);
    }
  }
}
function update_test_success() {
  $.ajax({
    url: "/releaseobject/process/test/update/",
    type: "GET",
    dataType: "JSON",
    data: {
      orgunit: orgunit,
      fixversion: fix_version,
      env: env,
    },
  });
  update_start_release_button_after_test(env);
}
function update_start_release_button_after_test(cur_env) {
  var start_button_text;
  var test_button;
  var test_button_text;
  if (env == "PIE") {
    start_button_text = "Start Release on STG";
    env = "STG";
  } else if (env == "STG") {
    start_button_text = "Start Release on PROD";
    env = "PROD";
  } else if (env == "PROD") {
    start_button_text = "Close Release";
    env = "RELEASED";
  }
  test_button = "#" + cur_env.toLowerCase() + "-test";
  test_button_text = cur_env + " tested";
  if (bux_test[cur_env] == "") {
    $("#start-release").text(start_button_text);
    $("#start-release").attr("disabled", false);
    $(test_button).text(test_button_text);
    $(test_button).css({
      "background-color": "#21BA45",
      "border-color": "#21BA45",
    });
    $(test_button).attr("data-bs-toggle", "");
    $(test_button).attr("data-bs-target", "");
    bux_test[cur_env] = "tested";
  }
}
function update_success_text() {
  if (env == "PIE") {
    $("#test-pass").html("Test done on <strong>BUX PIE</strong>");
  } else if (env == "STG") {
    $("#test-pass").html("Test done on <strong>BUX STG</strong>");
  } else if (env == "PROD") {
    $("#test-pass").html("Test done on <strong>BUX PROD</strong>");
  }
}
function button_flash(id, action) {
  if (action == "stop" || id.includes("-test")) {
    running_id = "";
    if (typeof timeId != "undefined") {
      clearInterval(timeId);
    }
    $(id).css({ opacity: 1 });
  } else {
    var opacity = 0;
    var interval = 0.5;
    timeId = setInterval(function () {
      running_id = id;
      opacity = opacity + interval;
      if (opacity == 10) {
        interval = 0.5;
      }
      if (opacity == 20) {
        interval = -0.5;
      }
      $(id).css({ opacity: opacity / 20 });
    }, 50);
  }
}
function set_step_offcanvas(button_id, tracker) {
  var button_id = "#" + key;
  $(button_id).attr("data-bs-toggle", "offcanvas");
  $(button_id).attr("href", "#step_details_deploy");
  $(button_id).attr("role", "button");
  $(button_id).attr("aria-controls", "offcanvasStart");
  var details_title = orgunit + " " + fix_version + " " + env;
  var time_start = tracker[key]["start"];
  var time_complete = tracker[key]["completed"];
  var details_body = "";
  if (time_complete == "") {
    details_body = time_start + " started<br>";
  } else {
    details_body =
      time_start + " started<br>" + time_complete + " completed";
  }
  $("#rop-step-details-title").html(details_title);
  $("#rop-step-details-body").html(details_body);
}
function save_rp_components() {}
function update_offcanvas_deploy_details_component(ro) {
  for (var index = 0; index < bux_deployment_sub_env.length; index++) {
    var detail_element =
      "#rp_step_detail_" +
      bux_deployment_sub_env[index].toLowerCase() +
      "_deploy";
    $(detail_element).empty();
    for (component_name in ro[fix_version]) {
      octo_project_name = component_name.replace("_", "-");
      release_version = ro[fix_version][component_name]["releaseversion"];
      td =
        "\
    <td>\
      <a href=https://octopus.nextestate.com/app#/" +
        octo_space +
        "/projects/" +
        octo_project_name +
        "/deployments/releases/" +
        release_version +
        ">" +
        component_name +
        "</a>\
    </td>";
      td +=
        "<td id=" +
        bux_deployment_sub_env[index].toLowerCase() +
        "_state_" +
        component_name.toLowerCase() +
        "></td>";
      td +=
        "<td id=" +
        bux_deployment_sub_env[index].toLowerCase() +
        "_duration_" +
        component_name.toLowerCase() +
        "></td>";
      tr = "<tr>" + td + "</tr>";
      $(detail_element).append(tr);
    }
  }
}
function update_offcanvas_deploy_details_state(tracker) {
  for (key in tracker) {
    if (key.includes("-deploy")) {
      var index = key.indexOf("-");
      var sub_env = key.substring(0, index);
      var tasks = tracker[key]["details"]["octopus"]["task_info"];
      for (var task in tasks) {
        var state_id =
          "#" +
          sub_env +
          "_state_" +
          tasks[task]["project_name"].toLowerCase();
        var duration_id =
          "#" +
          sub_env +
          "_duration_" +
          tasks[task]["project_name"].toLowerCase();
        $(state_id).text(tasks[task]["state"]);
        $(duration_id).text(tasks[task]["duration"]);
      }
    }
  }
}
function hide_all_detail_element() {
  $("#rp_step_detail_pie_deploy").css({ display: "none" });
  $("#rp_step_detail_stg2_deploy").css({ display: "none" });
  $("#rp_step_detail_stg1_deploy").css({ display: "none" });
  $("#rp_step_detail_dc2_deploy").css({ display: "none" });
  $("#rp_step_detail_dc1_deploy").css({ display: "none" });
  $("#rp_step_detail_stg2_disable_prt").css({ display: "none" });
  $("#rp_step_detail_stg1_disable_prt").css({ display: "none" });
  $("#rp_step_detail_stg2_disable_nonprt").css({ display: "none" });
  $("#rp_step_detail_stg1_disable_nonprt").css({ display: "none" });
  $("#rp_step_detail_dc2_disable_prt").css({ display: "none" });
  $("#rp_step_detail_dc1_disable_prt").css({ display: "none" });
  $("#rp_step_detail_dc2_disable_nonprt").css({ display: "none" });
  $("#rp_step_detail_dc1_disable_nonprt").css({ display: "none" });
  $("#rp_step_detail_dc2_drain_prt").css({ display: "none" });
  $("#rp_step_detail_dc1_drain_prt").css({ display: "none" });
  $("#rp_step_detail_dc2_drain_nonprt").css({ display: "none" });
  $("#rp_step_detail_dc1_drain_nonprt").css({ display: "none" });
}
function show_running_env_deploy_detail(running_env) {
  hide_all_detail_element();
  var table_header =
    "<tr><th>Component</th><th>State</th><th>Duration</th></tr>";
  $("#rp_step_detail_theader").html(table_header);
  var detail_element =
    "#rp_step_detail_" + running_env.toLowerCase() + "_deploy";
  $(detail_element).css({ display: "table-row-group" });
}
function show_running_env_disable_detail(prt, running_env) {
  hide_all_detail_element();
  var table_header = "<tr><th>Pool</th><th>State</th></tr>";
  $("#rp_step_detail_theader").html(table_header);
  var detail_element =
    "#rp_step_detail_" + running_env.toLowerCase() + "_disable_" + prt;
  $(detail_element).css({ display: "table-row-group" });
}
function show_running_env_drain_detail(prt, running_env) {
  hide_all_detail_element();
  var table_header = "<tr><th>Member</th><th>Connection</th></tr>";
  $("#rp_step_detail_theader").html(table_header);
  var detail_element =
    "#rp_step_detail_" + running_env.toLowerCase() + "_drain_" + prt;
  $(detail_element).css({ display: "table-row-group" });
}