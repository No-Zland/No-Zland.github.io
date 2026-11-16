Blockly.Blocks['1752581102357'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581102357",
      "message0": "大右走",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581102357'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,100,113,70,123,98,123,188,10,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(58,24,190,53,102,40,148,81,123,188,10,115,85,130,77,136,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(58,24,190,93,113,70,123,94,123,188,10,102,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(58,24,190,100,113,70,123,98,123,188,10,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752581102357'] = function(block) {
  let code = "robot.leju_action('大右走')\n";
  return code;
}

