// Copyright 2014 Team 254. All Rights Reserved.
// Author: pat@patfairbank.com (Patrick Fairbank)
// Author: nick@team254.com (Nick Eyre)
//
// Client-side methods for the audience display.

var websocket;
let transitionMap;
const transitionQueue = [];
let transitionInProgress = false;
let currentScreen = "blank";
let redSide;
let blueSide;
let currentMatch;
let overlayCenteringHideParams;
let overlayCenteringShowParams;
const allianceSelectionTemplate = Handlebars.compile($("#allianceSelectionTemplate").html());
const sponsorImageTemplate = Handlebars.compile($("#sponsorImageTemplate").html());
const sponsorTextTemplate = Handlebars.compile($("#sponsorTextTemplate").html());

// Constants for overlay positioning. The CSS is the source of truth for the values that represent initial state.
const overlayCenteringTopUp = "-130px";
const overlayCenteringBottomHideParams = {queue: false, bottom: $("#overlayCentering").css("bottom")};
const overlayCenteringBottomShowParams = {queue: false, bottom: "0px"};
const overlayCenteringTopHideParams = {queue: false, top: overlayCenteringTopUp};
const overlayCenteringTopShowParams = {queue: false, top: "50px"};
const eventMatchInfoDown = "30px";
const eventMatchInfoUp = $("#eventMatchInfo").css("height");
const logoUp = "23px";
const logoDown = $("#logo").css("top");
const scoreIn = $(".score").css("width");
const scoreMid = "185px";
const scoreOut = "400px";
const scoreFieldsOut = "180px";
const scoreLogoTop = "-470px";
const bracketLogoTop = "-780px";
const bracketLogoScale = 0.75;
const timeoutDetailsIn = $("#timeoutDetails").css("width");
const timeoutDetailsOut = "570px";

// Game-specific constants and variables.
const amplifyProgressStartOffset = $("#leftAmplified svg circle").css("stroke-dashoffset");
const amplifyFadeTimeMs = 300;
const amplifyDwellTimeMs = 500;
let redAmplified = false;
let blueAmplified = false;

// Handles a websocket message to change which screen is displayed.
const handleAudienceDisplayMode = function(targetScreen) {
  transitionQueue.push(targetScreen);
  executeTransitionQueue();
};

// Sequentially executes all transitions in the queue. Returns without doing anything if another invocation is already
// in progress.
const executeTransitionQueue = function() {
  if (transitionInProgress) {
    // There is an existing invocation of this method which will execute all transitions in the queue.
    return;
  }

  if (transitionQueue.length > 0) {
    transitionInProgress = true;
    const targetScreen = transitionQueue.shift();
    const callback = function() {
      // When the current transition is complete, call this method again to invoke the next one in the queue.
      currentScreen = targetScreen;
      transitionInProgress = false;
      setTimeout(executeTransitionQueue, 100);  // A small delay is needed to avoid visual glitches.
    };

    if (targetScreen === currentScreen) {
      callback();
      return;
    }

    if (targetScreen === "sponsor") {
      initializeSponsorDisplay();
    }

    let transitions = transitionMap[currentScreen][targetScreen];
    if (transitions !== undefined) {
      transitions(callback);
    } else {
      // There is no direct transition defined; need to go to the blank screen first.
      transitionMap[currentScreen]["blank"](function() {
        transitionMap["blank"][targetScreen](callback);
      });
    }
  }
};

// Handles a websocket message to update the teams for the current match.
const handleMatchLoad = function(data) {
  currentMatch = data.match;
  $(`#${redSide}Team1`).text(currentMatch.red1);
  $(`#${redSide}Team1`).attr("data-yellow-card", data.teams["R1"]?.yellow_card);
  $(`#${redSide}Team2`).text(currentMatch.red2);
  $(`#${redSide}Team2`).attr("data-yellow-card", data.teams["R2"]?.yellow_card);
  $(`#${redSide}Team3`).text(currentMatch.red3);
  $(`#${redSide}Team3`).attr("data-yellow-card", data.teams["R3"]?.yellow_card);
  $(`#${redSide}Team1Avatar`).attr("src", getAvatarUrl(currentMatch.red1));
  $(`#${redSide}Team2Avatar`).attr("src", getAvatarUrl(currentMatch.red2));
  $(`#${redSide}Team3Avatar`).attr("src", getAvatarUrl(currentMatch.red3));
  $(`#${blueSide}Team1`).text(currentMatch.blue1);
  $(`#${blueSide}Team1`).attr("data-yellow-card", data.teams["B1"]?.yellow_card);
  $(`#${blueSide}Team2`).text(currentMatch.blue2);
  $(`#${blueSide}Team2`).attr("data-yellow-card", data.teams["B2"]?.yellow_card);
  $(`#${blueSide}Team3`).text(currentMatch.blue3);
  $(`#${blueSide}Team3`).attr("data-yellow-card", data.teams["B3"]?.yellow_card);
  $(`#${blueSide}Team1Avatar`).attr("src", getAvatarUrl(currentMatch.blue1));
  $(`#${blueSide}Team2Avatar`).attr("src", getAvatarUrl(currentMatch.blue2));
  $(`#${blueSide}Team3Avatar`).attr("src", getAvatarUrl(currentMatch.blue3));

  // Show alliance numbers if this is a playoff match.
  if (currentMatch.Type === matchTypePlayoff) {
    $(`#${redSide}PlayoffAlliance`).text(currentMatch.playoff_red_alliance);
    $(`#${blueSide}PlayoffAlliance`).text(currentMatch.playoff_blue_alliance);
    $(".playoff-alliance").show();

    // Show the series status if this playoff round isn't just a single match.
    if (data.matchup.num_wins_to_advance > 1) {
      $(`#${redSide}PlayoffAllianceWins`).text(data.matchup.red_alliance_wins);
      $(`#${blueSide}PlayoffAllianceWins`).text(data.matchup.blue_alliance_wins);
      $("#playoffSeriesStatus").css("display", "flex");
    } else {
      $("#playoffSeriesStatus").hide();
    }
  } else {
    $(`#${redSide}PlayoffAlliance`).text("");
    $(`#${blueSide}PlayoffAlliance`).text("");
    $(".playoff-alliance").hide();
    $("#playoffSeriesStatus").hide();
  }

  let matchName = data.match.long_name;
  if (data.match.name_detail !== "") {
    matchName += " &ndash; " + data.match.name_detail;
  }
  $("#matchName").html(matchName);
  $("#timeoutNextMatchName").html(matchName);
  $("#timeoutBreakDescription").text(data.break_description);
};

// Handles a websocket message to update the match time countdown.
const handleMatchTime = function(data) {
  translateMatchTime(data, function(matchState, matchStateText, countdownSec) {
    $("#matchTime").text(getCountdownString(countdownSec));
  });
};

// Handles a websocket message to update the match score.
const handleRealtimeScore = function(data) {
  $(`#${redSide}ScoreNumber`).text(data.red.score_summary.score - data.red.score_summary.barge_points);
  $(`#${blueSide}ScoreNumber`).text(data.blue.score_summary.score - data.blue.score_summary.barge_points);

  $(`#${redSide}NoteNumerator`).text(data.red.score_summary.num_coral_levels_met);
  $(`#${redSide}NoteDenominator`).text(data.red.score_summary.num_coral_levels_goal);
  $(`#${blueSide}NoteNumerator`).text(data.blue.score_summary.num_coral_levels_met);
  $(`#${blueSide}NoteDenominator`).text(data.blue.score_summary.num_coral_levels_goal);
  if (currentMatch.type === matchTypePlayoff) {
    $(`#${redSide}NoteDenominator`).hide();
    $(`#${blueSide}NoteDenominator`).hide();
    $(".note-splitter").hide();
  } else {
    $(`#${redSide}NoteDenominator`).show();
    $(`#${blueSide}NoteDenominator`).show();
    $(".note-splitter").show();
  }
};

// Handles a websocket message to populate the final score data.
const handleScorePosted = function(data) {
  $(`#${redSide}FinalScore`).text(data.red_score_summary.score);
  $(`#${redSide}FinalAlliance`).text("Alliance " + data.match.playoff_red_alliance);
  setTeamInfo(redSide, 1, data.match.red1, data.red_cards, data.red_rankings);
  setTeamInfo(redSide, 2, data.match.red2, data.red_cards, data.red_rankings);
  setTeamInfo(redSide, 3, data.match.red3, data.red_cards, data.red_rankings);
  if (data.red_off_field_team_ids.length > 0) {
    setTeamInfo(redSide, 4, data.red_off_field_teams_ids[0], data.red_cards, data.red_rankings);
  } else {
    setTeamInfo(redSide, 4, 0, data.red_cards, data.red_rankings);
  }
  $(`#${redSide}FinalLeavePoints`).text(data.red_score_summary.leave_points);
  $(`#${redSide}FinalSpeakerPoints`).text(data.red_score_summary.coral_points);
  $(`#${redSide}FinalAmpPoints`).text(data.red_score_summary.algae_points);
  $(`#${redSide}FinalStagePoints`).text(data.red_score_summary.barge_points);
  $(`#${redSide}FinalFoulPoints`).text(data.red_score_summary.foul_points);
  $(`#${redSide}FinalAutoBonusRankingPoint`).html(
    data.red_score_summary.auto_bonus_ranking_point ? "&#x2714;" : "&#x2718;"
  );
  $(`#${redSide}FinalAutoBonusRankingPoint`).attr(
    "data-checked", data.red_score_summary.auto_bonus_ranking_point
  );
  $(`#${redSide}FinalMelodyBonusRankingPoint`).html(
    data.red_score_summary.coral_bonus_ranking_point ? "&#x2714;" : "&#x2718;"
  );
  $(`#${redSide}FinalMelodyBonusRankingPoint`).attr(
    "data-checked", data.red_score_summary.coral_bonus_ranking_point
  );
  $(`#${redSide}FinalEnsembleBonusRankingPoint`).html(
    data.red_score_summary.barge_bonus_ranking_point ? "&#x2714;" : "&#x2718;"
  );
  $(`#${redSide}FinalEnsembleBonusRankingPoint`).attr(
    "data-checked", data.red_score_summary.barge_bonus_ranking_point
  );
  $(`#${redSide}FinalRankingPoints`).html(data.red_ranking_points);
  $(`#${redSide}FinalWins`).text(data.red_wins);
  const redFinalDestination = $(`#${redSide}FinalDestination`);
  redFinalDestination.html(data.red_destination.replace("Advances to ", "Advances to<br>"));
  redFinalDestination.toggle(data.red_destination !== "");
  redFinalDestination.attr("data-won", data.red_won);

  $(`#${blueSide}FinalScore`).text(data.blue_score_summary.score);
  $(`#${blueSide}FinalAlliance`).text("Alliance " + data.match.playoff_blue_alliance);
  setTeamInfo(blueSide, 1, data.match.blue1, data.blue_cards, data.blue_rankings);
  setTeamInfo(blueSide, 2, data.match.blue2, data.blue_cards, data.blue_rankings);
  setTeamInfo(blueSide, 3, data.match.blue3, data.blue_cards, data.blue_rankings);
  if (data.blue_off_field_team_ids.length > 0) {
    setTeamInfo(blueSide, 4, data.blue_off_field_team_ids[0], data.blue_cards, data.blue_rankings);
  } else {
    setTeamInfo(blueSide, 4, 0, data.blue_cards, data.blue_rankings);
  }
  $(`#${blueSide}FinalLeavePoints`).text(data.blue_score_summary.leave_points);
  $(`#${blueSide}FinalSpeakerPoints`).text(data.blue_score_summary.coral_points);
  $(`#${blueSide}FinalAmpPoints`).text(data.blue_score_summary.algae_points);
  $(`#${blueSide}FinalStagePoints`).text(data.blue_score_summary.barge_points);
  $(`#${blueSide}FinalFoulPoints`).text(data.blue_score_summary.foul_points);
  $(`#${blueSide}FinalAutoBonusRankingPoint`).html(
    data.blue_score_summary.auto_bonus_ranking_point ? "&#x2714;" : "&#x2718;"
  );
  $(`#${blueSide}FinalAutoBonusRankingPoint`).attr(
    "data-checked", data.blue_score_summary.auto_bonus_ranking_point
  );
  $(`#${blueSide}FinalMelodyBonusRankingPoint`).html(
    data.blue_score_summary.coral_bonus_ranking_point ? "&#x2714;" : "&#x2718;"
  );
  $(`#${blueSide}FinalMelodyBonusRankingPoint`).attr(
    "data-checked", data.blue_score_summary.coral_bonus_ranking_point
  );
  $(`#${blueSide}FinalEnsembleBonusRankingPoint`).html(
    data.blue_score_summary.barge_bonus_ranking_point ? "&#x2714;" : "&#x2718;"
  );
  $(`#${blueSide}FinalEnsembleBonusRankingPoint`).attr(
    "data-checked", data.blue_score_summary.barge_bonus_ranking_point
  );
  $(`#${blueSide}FinalRankingPoints`).html(data.blue_ranking_points);
  $(`#${blueSide}FinalWins`).text(data.blue_wins);
  const blueFinalDestination = $(`#${blueSide}FinalDestination`);
  blueFinalDestination.html(data.blue_destination.replace("Advances to ", "Advances to<br>"));
  blueFinalDestination.toggle(data.blue_destination !== "");
  blueFinalDestination.attr("data-won", data.blue_won);

  let matchName = data.match.long_name;
  if (data.match.name_detail !== "") {
    matchName += " &ndash; " + data.match.name_detail;
  }
  $("#finalMatchName").html(matchName);

  // Reload the bracket to reflect any changes.
  $("#bracketSvg").attr("src", "/api/bracket/svg?activeMatch=saved&v=" + new Date().getTime());

  if (data.match.type === matchTypePlayoff) {
    // Hide bonus ranking points and show playoff-only fields.
    $(".playoff-hidden-field").hide();
    $(".playoff-only-field").show();
  } else {
    $(".playoff-hidden-field").show();
    $(".playoff-only-field").hide();
  }
};

// Handles a websocket message to play a sound to signal match start/stop/etc.
const handlePlaySound = function(sound) {
  $("audio").each(function(k, v) {
    // Stop and reset any sounds that are still playing.
    v.pause();
    v.currentTime = 0;
  });
  $("#sound-" + sound)[0].play();
};

// Handles a websocket message to update the alliance selection screen.
const handleAllianceSelection = function(data) {
  const alliances = data.alliances;
  const rankedTeams = data.ranked_teams;
  if (alliances && alliances.length > 0) {
    const numColumns = alliances[0].team_ids.length + 1;
    $.each(alliances, function(k, v) {
      v.index = k + 1;
    });
    $("#allianceSelection").html(allianceSelectionTemplate({alliances: alliances, numColumns: numColumns}));
  }
  if (rankedTeams) {
      let text = "";
      $.each(rankedTeams, function(i, v) {
        if (!v.Picked) {
          text += `<div class="unpicked"><div class="unpicked-rank">${v.rank}.</div>` +
            `<div class="unpicked-team">${v.team_id}</div></div>`;
        }
      });
      $("#allianceRankings").html(text);
  }

  if (data.show_timer) {
    $("#allianceSelectionTimer").text(getCountdownString(data.time_remaining_sec));
  } else {
    $("#allianceSelectionTimer").html("&nbsp;");
  }
};

// Handles a websocket message to populate and/or show/hide a lower third.
const handleLowerThird = function(data) {
  if (data.lower_third !== null) {
    if (data.lower_third.bottom_text === "") {
      $("#lowerThirdTop").hide();
      $("#lowerThirdBottom").hide();
      $("#lowerThirdSingle").text(data.lower_third.top_text);
      $("#lowerThirdSingle").show();
    } else {
      $("#lowerThirdSingle").hide();
      $("#lowerThirdTop").text(data.lower_third.top_text);
      $("#lowerThirdBottom").text(data.lower_third.bottom_text);
      $("#lowerThirdTop").show();
      $("#lowerThirdBottom").show();
    }
  }

  const lowerThirdElement = $("#lowerThird");
  if (data.show_lower_third && !lowerThirdElement.is(":visible")) {
    lowerThirdElement.show();
    lowerThirdElement.transition({queue: false, left: "150px"}, 750, "ease");
  } else if (!data.show_lower_third && lowerThirdElement.is(":visible")) {
    lowerThirdElement.transition({queue: false, left: "-1000px"}, 1000, "ease", function () {
      lowerThirdElement.hide();
    });
  }
};

const transitionAllianceSelectionToBlank = function(callback) {
  $('#allianceSelectionCentering').transition({queue: false, right: "-60em"}, 500, "ease", callback);
  $('#allianceRankingsCentering.enabled').transition({queue:false, left: "-60em"}, 500, "ease");
};

const transitionBlankToAllianceSelection = function(callback) {
  $('#allianceSelectionCentering').css("right","-60em").show();
  $('#allianceSelectionCentering').transition({queue: false, right: "3em"}, 500, "ease", callback);
  $('#allianceRankingsCentering.enabled').css("left", "-60em").show();
  $('#allianceRankingsCentering.enabled').transition({queue: false, left: "3em"}, 500, "ease");
};

const transitionBlankToBracket = function(callback) {
  transitionBlankToLogo(function() {
    setTimeout(function() { transitionLogoToBracket(callback); }, 50);
  });
};

const transitionBlankToIntro = function(callback) {
  $("#overlayCentering").transition(overlayCenteringShowParams, 500, "ease", function() {
    $(".teams").css("display", "flex");
    $(".avatars").css("display", "flex");
    $(".avatars").css("opacity", 1);
    $(".score").transition({queue: false, width: scoreMid}, 500, "ease", function() {
      $("#eventMatchInfo").css("display", "flex");
      $("#eventMatchInfo").transition({queue: false, height: eventMatchInfoDown}, 500, "ease", callback);
    });
  });
};

const transitionBlankToLogo = function(callback) {
  $(".blindsCenter.blank").css({rotateY: "0deg"});
  $(".blindsCenter.full").css({rotateY: "-180deg"});
  $(".blinds.right").transition({queue: false, right: 0}, 1000, "ease");
  $(".blinds.left").transition({queue: false, left: 0}, 1000, "ease", function() {
    $(".blinds.left").addClass("full");
    $(".blinds.right").hide();
    setTimeout(function() {
      $(".blindsCenter.blank").transition({queue: false, rotateY: "180deg"}, 500, "ease");
      $(".blindsCenter.full").transition({queue: false, rotateY: "0deg"}, 500, "ease", callback);
    }, 200);
  });
};

const transitionBlankToLogoLuma = function(callback) {
  $(".blindsCenter.blank").css({rotateY: "180deg"});
  $(".blindsCenter.full").transition({ queue: false, rotateY: "0deg" }, 1000, "ease", callback);
};

const transitionBlankToMatch = function(callback) {
  $("#overlayCentering").transition(overlayCenteringShowParams, 500, "ease", function() {
    $(".teams").css("display", "flex");
    $(".score-fields").css("display", "flex");
    $(".score-fields").transition({queue: false, width: scoreFieldsOut}, 500, "ease");
    $("#logo").transition({queue: false, top: logoUp}, 500, "ease");
    $(".score").transition({queue: false, width: scoreOut}, 500, "ease", function() {
      $("#eventMatchInfo").css("display", "flex");
      $("#eventMatchInfo").transition({queue: false, height: eventMatchInfoDown}, 500, "ease", callback);
      $(".score-number").transition({queue: false, opacity: 1}, 750, "ease");
      $("#matchTime").transition({queue: false, opacity: 1}, 750, "ease");
      $(".score-fields").transition({queue: false, opacity: 1}, 750, "ease");
    });
  });
};

const transitionBlankToScore = function(callback) {
  transitionBlankToLogo(function() {
    setTimeout(function() { transitionLogoToScore(callback); }, 50);
  });
};

const transitionBlankToSponsor = function(callback) {
  $(".blindsCenter.blank").css({rotateY: "90deg"});
  $(".blinds.right").transition({queue: false, right: 0}, 1000, "ease");
  $(".blinds.left").transition({queue: false, left: 0}, 1000, "ease", function() {
    $(".blinds.left").addClass("full");
    $(".blinds.right").hide();
    setTimeout(function() {
      $("#sponsor").show();
      $("#sponsor").transition({queue: false, opacity: 1}, 1000, "ease", callback);
    }, 200);
  });
};

const transitionBlankToTimeout = function(callback) {
  $("#overlayCentering").transition(overlayCenteringShowParams, 500, "ease", function () {
    $("#timeoutDetails").transition({queue: false, width: timeoutDetailsOut}, 500, "ease");
    $("#logo").transition({queue: false, top: logoUp}, 500, "ease", function() {
      $(".timeout-detail").transition({queue: false, opacity: 1}, 750, "ease");
      $("#matchTime").transition({queue: false, opacity: 1}, 750, "ease", callback);
    });
  });
};

const transitionBracketToBlank = function(callback) {
  transitionBracketToLogo(function() {
    transitionLogoToBlank(callback);
  });
};

const transitionBracketToLogo = function(callback) {
  $("#bracket").transition({queue: false, opacity: 0}, 500, "ease", function(){
    $("#bracket").hide();
  });
  $(".blindsCenter.full").transition({queue: false, top: 0, scale: 1}, 625, "ease", callback);
};

const transitionBracketToLogoLuma = function(callback) {
  transitionBracketToLogo(function() {
    transitionLogoToLogoLuma(callback);
  });
};

const transitionBracketToScore = function(callback) {
  $(".blindsCenter.full").transition({queue: false, top: scoreLogoTop, scale: 1}, 1000, "ease");
  $("#bracket").transition({queue: false, opacity: 0}, 1000, "ease", function(){
    $("#bracket").hide();
    $("#finalScore").show();
    $("#finalScore").transition({queue: false, opacity: 1}, 1000, "ease", callback);
  });
};

const transitionBracketToSponsor = function(callback) {
  transitionBracketToLogo(function() {
    transitionLogoToSponsor(callback);
  });
};

const transitionIntroToBlank = function(callback) {
  $("#eventMatchInfo").transition({queue: false, height: eventMatchInfoUp}, 500, "ease", function() {
    $("#eventMatchInfo").hide();
    $(".score").transition({queue: false, width: scoreIn}, 500, "ease", function() {
      $(".avatars").css("opacity", 0);
      $(".avatars").hide();
      $(".teams").hide();
      $("#overlayCentering").transition(overlayCenteringHideParams, 1000, "ease", callback);
    });
  });
};

const transitionIntroToMatch = function(callback) {
  $(".avatars").transition({queue: false, opacity: 0}, 500, "ease", function() {
    $(".avatars").hide();
  });
  $(".score-fields").css("display", "flex");
  $(".score-fields").transition({queue: false, width: scoreFieldsOut}, 500, "ease");
  $("#logo").transition({queue: false, top: logoUp}, 500, "ease");
  $(".score").transition({queue: false, width: scoreOut}, 500, "ease", function() {
    $(".score-number").transition({queue: false, opacity: 1}, 750, "ease");
    $("#matchTime").transition({queue: false, opacity: 1}, 750, "ease", callback);
    $(".score-fields").transition({queue: false, opacity: 1}, 750, "ease");
  });
};

const transitionIntroToTimeout = function(callback) {
  $("#eventMatchInfo").transition({queue: false, height: eventMatchInfoUp}, 500, "ease", function() {
    $("#eventMatchInfo").hide();
    $(".score").transition({queue: false, width: scoreIn}, 500, "ease", function() {
      $(".avatars").css("opacity", 0);
      $(".avatars").hide();
      $(".teams").hide();
      $("#timeoutDetails").transition({queue: false, width: timeoutDetailsOut}, 500, "ease");
      $("#logo").transition({queue: false, top: logoUp}, 500, "ease", function() {
        $(".timeout-detail").transition({queue: false, opacity: 1}, 750, "ease");
        $("#matchTime").transition({queue: false, opacity: 1}, 750, "ease", callback);
      });
    });
  });
};

const transitionLogoToBlank = function(callback) {
  $(".blindsCenter.blank").transition({queue: false, rotateY: "360deg"}, 500, "ease");
  $(".blindsCenter.full").transition({queue: false, rotateY: "180deg"}, 500, "ease", function() {
    setTimeout(function() {
      $(".blinds.left").removeClass("full");
      $(".blinds.right").show();
      $(".blinds.right").transition({queue: false, right: "-50%"}, 1000, "ease");
      $(".blinds.left").transition({queue: false, left: "-50%"}, 1000, "ease", callback);
    }, 200);
  });
};

const transitionLogoToBracket = function(callback) {
  $(".blindsCenter.full").transition({queue: false, top: bracketLogoTop, scale: bracketLogoScale}, 625, "ease");
  $("#bracket").show();
  $("#bracket").transition({queue: false, opacity: 1}, 1000, "ease", callback);
};

const transitionLogoToLogoLuma = function(callback) {
  $(".blinds.left").removeClass("full");
  $(".blinds.right").show();
  $(".blinds.right").transition({queue: false, right: "-50%"}, 1000, "ease");
  $(".blinds.left").transition({queue: false, left: "-50%"}, 1000, "ease", function() {
    if (callback) {
      callback();
    }
  });
};

const transitionLogoToScore = function(callback) {
  $(".blindsCenter.full").transition({queue: false, top: scoreLogoTop}, 625, "ease");
  $("#finalScore").show();
  $("#finalScore").transition({queue: false, opacity: 1}, 1000, "ease", callback);
};

const transitionLogoToSponsor = function(callback) {
  $(".blindsCenter.full").transition({queue: false, rotateY: "90deg"}, 750, "ease", function () {
    $("#sponsor").show();
    $("#sponsor").transition({queue: false, opacity: 1}, 1000, "ease", callback);
  });
};

const transitionLogoLumaToBlank = function(callback) {
  $(".blindsCenter.full").transition({queue: false, rotateY: "180deg"}, 1000, "ease", callback);
};

const transitionLogoLumaToBracket = function(callback) {
  transitionLogoLumaToLogo(function() {
    transitionLogoToBracket(callback);
  });
};

const transitionLogoLumaToLogo = function(callback) {
  $(".blinds.right").transition({queue: false, right: 0}, 1000, "ease");
  $(".blinds.left").transition({queue: false, left: 0}, 1000, "ease", function() {
    $(".blinds.left").addClass("full");
    $(".blinds.right").hide();
    if (callback) {
      callback();
    }
  });
};

const transitionLogoLumaToScore = function(callback) {
  transitionLogoLumaToLogo(function() {
    transitionLogoToScore(callback);
  });
};

const transitionMatchToBlank = function(callback) {
  $("#eventMatchInfo").transition({queue: false, height: eventMatchInfoUp}, 500, "ease");
  $("#matchTime").transition({queue: false, opacity: 0}, 300, "linear");
  $(".score-fields").transition({queue: false, opacity: 0}, 300, "ease");
  $(".score-number").transition({queue: false, opacity: 0}, 300, "linear", function() {
    $("#eventMatchInfo").hide();
    $(".score-fields").transition({queue: false, width: 0}, 500, "ease");
    $("#logo").transition({queue: false, top: logoDown}, 500, "ease");
    $(".score").transition({queue: false, width: scoreIn}, 500, "ease", function() {
      $(".teams").hide();
      $(".score-fields").hide();
      $("#overlayCentering").transition(overlayCenteringHideParams, 1000, "ease", callback);
    });
  });
};

const transitionMatchToIntro = function(callback) {
  $(".score-number").transition({queue: false, opacity: 0}, 300, "linear");
  $(".score-fields").transition({queue: false, opacity: 0}, 300, "ease");
  $("#matchTime").transition({queue: false, opacity: 0}, 300, "linear", function() {
    $(".score-fields").transition({queue: false, width: 0}, 500, "ease");
    $("#logo").transition({queue: false, top: logoDown}, 500, "ease");
    $(".score").transition({queue: false, width: scoreMid}, 500, "ease", function() {
      $(".score-fields").hide();
      $(".avatars").css("display", "flex");
      $(".avatars").transition({queue: false, opacity: 1}, 500, "ease", callback);
    });
  });
};

const transitionScoreToBlank = function(callback) {
  transitionScoreToLogo(function() {
    transitionLogoToBlank(callback);
  });
};

const transitionScoreToBracket = function(callback) {
  $(".blindsCenter.full").transition({queue: false, top: bracketLogoTop, scale: bracketLogoScale}, 1000, "ease");
  $("#finalScore").transition({queue: false, opacity: 0}, 1000, "ease", function(){
    $("#finalScore").hide();
    $("#bracket").show();
    $("#bracket").transition({queue: false, opacity: 1}, 1000, "ease", callback);
  });
};

const transitionScoreToLogo = function(callback) {
  $("#finalScore").transition({queue: false, opacity: 0}, 500, "ease", function(){
    $("#finalScore").hide();
  });
  $(".blindsCenter.full").transition({queue: false, top: 0}, 625, "ease", callback);
};

const transitionScoreToLogoLuma = function(callback) {
  transitionScoreToLogo(function() {
    transitionLogoToLogoLuma(callback);
  });
};

const transitionScoreToSponsor = function(callback) {
  transitionScoreToLogo(function() {
    transitionLogoToSponsor(callback);
  });
};

const transitionSponsorToBlank = function(callback) {
  $("#sponsor").transition({queue: false, opacity: 0}, 1000, "ease", function() {
    setTimeout(function() {
      $(".blinds.left").removeClass("full");
      $(".blinds.right").show();
      $(".blinds.right").transition({queue: false, right: "-50%"}, 1000, "ease");
      $(".blinds.left").transition({queue: false, left: "-50%"}, 1000, "ease", callback);
      $("#sponsor").hide();
    }, 200);
  });
};

const transitionSponsorToBracket = function(callback) {
  transitionSponsorToLogo(function() {
    transitionLogoToBracket(callback);
  });
};

const transitionSponsorToLogo = function(callback) {
  $("#sponsor").transition({queue: false, opacity: 0}, 1000, "ease", function() {
    $(".blindsCenter.full").transition({queue: false, rotateY: "0deg"}, 750, "ease", callback);
    $("#sponsor").hide();
  });
};

const transitionSponsorToScore = function(callback) {
  transitionSponsorToLogo(function() {
    transitionLogoToScore(callback);
  });
};

const transitionTimeoutToBlank = function(callback) {
  $(".timeout-detail").transition({queue: false, opacity: 0}, 300, "linear");
  $("#matchTime").transition({queue: false, opacity: 0}, 300, "linear", function() {
    $("#timeoutDetails").transition({queue: false, width: timeoutDetailsIn}, 500, "ease");
    $("#logo").transition({queue: false, top: logoDown}, 500, "ease", function() {
      $("#overlayCentering").transition(overlayCenteringHideParams, 1000, "ease", callback);
    });
  });
};

const transitionTimeoutToIntro = function(callback) {
  $(".timeout-detail").transition({queue: false, opacity: 0}, 300, "linear");
  $("#matchTime").transition({queue: false, opacity: 0}, 300, "linear", function() {
    $("#timeoutDetails").transition({queue: false, width: timeoutDetailsIn}, 500, "ease");
    $("#logo").transition({queue: false, top: logoDown}, 500, "ease", function() {
      $(".avatars").css("display", "flex");
      $(".avatars").css("opacity", 1);
      $(".teams").css("display", "flex");
      $(".score").transition({queue: false, width: scoreMid}, 500, "ease", function () {
        $("#eventMatchInfo").show();
        $("#eventMatchInfo").transition({queue: false, height: eventMatchInfoDown}, 500, "ease", callback);
      });
    });
  });
};

// Loads sponsor slide data and builds the slideshow HTML.
const initializeSponsorDisplay = function() {
  $.getJSON("/api/sponsor_slides", function(slides) {
    $("#sponsorContainer").empty();

    // Inject the HTML for each slide into the DOM.
    $.each(slides, function(index, slide) {
      slide.DisplayTimeMs = slide.DisplayTimeSec * 1000;
      slide.First = index === 0;

      let slideHtml;
      if (slide.Image) {
        slideHtml = sponsorImageTemplate(slide);
      } else {
        slideHtml = sponsorTextTemplate(slide);
      }
      $("#sponsorContainer").append(slideHtml);
    });
  });
};

const getAvatarUrl = function(teamId) {
  return "/api/teams/" + teamId + "/avatar";
};

const setTeamInfo = function(side, position, teamId, cards, rankings) {
  const teamNumberElement = $(`#${side}FinalTeam${position}`);
  teamNumberElement.html(teamId);
  teamNumberElement.toggle(teamId > 0);
  const avatarElement = $(`#${side}FinalTeam${position}Avatar`);
  avatarElement.attr("src", getAvatarUrl(teamId));
  avatarElement.toggle(teamId > 0);

  const cardElement = $(`#${side}FinalTeam${position}Card`);
  cardElement.attr("data-card", cards[teamId.toString()] || "");

  const ranking = rankings[teamId];
  let rankIndicator = "";
  let rankNumber = "";
  if (ranking !== undefined && ranking !== null && ranking.Rank !== 0) {
    rankNumber = ranking.Rank;
    if (rankNumber > ranking.PreviousRank && ranking.PreviousRank > 0) {
      rankIndicator = "rank-down";
    } else if (rankNumber < ranking.PreviousRank) {
      rankIndicator = "rank-up";
    }
  }

  const rankIndicatorElement = $(`#${side}FinalTeam${position}RankIndicator`);
  rankIndicatorElement.attr("src", rankIndicator === "" ? "" : `/static/img/${rankIndicator}.svg`);
  rankIndicatorElement.toggle(rankIndicator !== "" && teamId > 0);

  const rankNumberElement = $(`#${side}FinalTeam${position}RankNumber`);
  rankNumberElement.text(rankNumber);
  rankNumberElement.toggle(teamId > 0);
};

$(function() {
  // Read the configuration for this display from the URL query string.
  const urlParams = new URLSearchParams(window.location.search);
  document.body.style.backgroundColor = urlParams.get("background");
  const reversed = urlParams.get("reversed");
  if (reversed === "true") {
    redSide = "right";
    blueSide = "left";
  } else {
    redSide = "left";
    blueSide = "right";
  }
  $(".reversible-left").attr("data-reversed", reversed);
  $(".reversible-right").attr("data-reversed", reversed);
  if (urlParams.get("overlayLocation") === "top") {
    overlayCenteringHideParams = overlayCenteringTopHideParams;
    overlayCenteringShowParams = overlayCenteringTopShowParams;
    $("#overlayCentering").css("top", overlayCenteringTopUp);
  } else {
    overlayCenteringHideParams = overlayCenteringBottomHideParams;
    overlayCenteringShowParams = overlayCenteringBottomShowParams;
  }

  // Set up the websocket back to the server.
  websocket = new wsHandler("/api/displays/audience/websocket", {
    alliance_selection: function(event) { handleAllianceSelection(event.data); },
    audience_display_mode: function(event) { handleAudienceDisplayMode(event.data); },
    lower_third: function(event) { handleLowerThird(event.data); },
    match_load: function(event) { handleMatchLoad(event.data); },
    match_time: function(event) { handleMatchTime(event.data); },
    match_timing: function(event) { handleMatchTiming(event.data); },
    play_sound: function(event) { handlePlaySound(event.data); },
    realtime_score: function(event) { handleRealtimeScore(event.data); },
    score_posted: function(event) { handleScorePosted(event.data); },
  });

  // Map how to transition from one screen to another. Missing links between screens indicate that first we
  // must transition to the blank screen and then to the target screen.
  transitionMap = {
    allianceSelection: {
      blank: transitionAllianceSelectionToBlank,
    },
    blank: {
      allianceSelection: transitionBlankToAllianceSelection,
      bracket: transitionBlankToBracket,
      intro: transitionBlankToIntro,
      logo: transitionBlankToLogo,
      logoLuma: transitionBlankToLogoLuma,
      match: transitionBlankToMatch,
      score: transitionBlankToScore,
      sponsor: transitionBlankToSponsor,
      timeout: transitionBlankToTimeout,
    },
    bracket: {
      blank: transitionBracketToBlank,
      logo: transitionBracketToLogo,
      logoLuma: transitionBracketToLogoLuma,
      score: transitionBracketToScore,
      sponsor: transitionBracketToSponsor,
    },
    intro: {
      blank: transitionIntroToBlank,
      match: transitionIntroToMatch,
      timeout: transitionIntroToTimeout,
    },
    logo: {
      blank: transitionLogoToBlank,
      bracket: transitionLogoToBracket,
      logoLuma: transitionLogoToLogoLuma,
      score: transitionLogoToScore,
      sponsor: transitionLogoToSponsor,
    },
    logoLuma: {
      blank: transitionLogoLumaToBlank,
      bracket: transitionLogoLumaToBracket,
      logo: transitionLogoLumaToLogo,
      score: transitionLogoLumaToScore,
    },
    match: {
      blank: transitionMatchToBlank,
      intro: transitionMatchToIntro,
    },
    score: {
      blank: transitionScoreToBlank,
      bracket: transitionScoreToBracket,
      logo: transitionScoreToLogo,
      logoLuma: transitionScoreToLogoLuma,
      sponsor: transitionScoreToSponsor,
    },
    sponsor: {
      blank: transitionSponsorToBlank,
      bracket: transitionSponsorToBracket,
      logo: transitionSponsorToLogo,
      score: transitionSponsorToScore,
    },
    timeout: {
      blank: transitionTimeoutToBlank,
      intro: transitionTimeoutToIntro,
    },
  }
});
