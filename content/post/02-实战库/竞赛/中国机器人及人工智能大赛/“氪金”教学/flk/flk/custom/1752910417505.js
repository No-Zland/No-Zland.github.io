Blockly.Blocks['1752910417505'] = {
  init: function() {
    this.jsonInit({
      "type": "1752910417505",
      "message0": "you1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752910417505'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,100,113,70,123,98,123,188,10,99,87,132,76,104,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,101,113,61,129,102,123,188,10,120,79,122,77,111,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(58,24,190,100,113,70,123,98,123,188,10,99,87,132,76,104,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752910417505'] = function(block) {
  let code = "robot.leju_action('you1')\n";
  return code;
}

