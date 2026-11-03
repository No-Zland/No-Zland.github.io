Blockly.Blocks['1752577768533'] = {
  init: function() {
    this.jsonInit({
      "type": "1752577768533",
      "message0": "叠块小右走",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752577768533'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,113,70,123,98,129,174,10,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,95,113,71,121,97,129,174,10,117,85,130,76,113,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(66,21,190,93,113,70,123,94,129,174,10,102,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(66,21,190,100,113,70,123,98,129,174,10,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752577768533'] = function(block) {
  let code = "robot.leju_action('叠块小右走')\n";
  return code;
}

