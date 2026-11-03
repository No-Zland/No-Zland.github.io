Blockly.Blocks['1752581168812'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581168812",
      "message0": "大左走",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581168812'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(58,24,180,100,93,55,124,100,123,188,22,99,107,144,75,99,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,180,75,109,78,117,69,123,188,22,144,85,117,82,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(58,24,180,93,113,70,123,94,123,188,22,102,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,180,96,113,70,123,94,123,188,22,95,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,180,100,113,70,123,94,123,188,22,98,87,132,76,104,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752581168812'] = function(block) {
  let code = "robot.leju_action('大左走')\n";
  return code;
}

