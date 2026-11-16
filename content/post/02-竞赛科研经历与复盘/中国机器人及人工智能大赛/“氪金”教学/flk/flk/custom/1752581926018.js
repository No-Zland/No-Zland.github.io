Blockly.Blocks['1752581926018'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581926018",
      "message0": "叠块左走",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581926018'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(58,24,180,100,93,55,124,100,123,188,22,99,107,144,75,99,120,40,99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(58,24,180,100,93,55,124,100,123,188,22,112,111,147,73,106,120,40,99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(58,24,180,100,93,55,124,100,123,188,22,99,107,144,75,99,120,40,99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752581926018'] = function(block) {
  let code = "robot.leju_action('叠块左走')\n";
  return code;
}

