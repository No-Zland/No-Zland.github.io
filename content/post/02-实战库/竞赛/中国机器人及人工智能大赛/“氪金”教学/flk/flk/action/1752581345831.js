Blockly.Blocks['1752581345831'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581345831",
      "message0": "大右转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581345831'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,87,114,34,172,90,123,188,10,108,149,157,104,108,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,100,93,55,124,100,123,188,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752581345831'] = function(block) {
  let code = "robot.leju_action('大右转')\n";
  return code;
}

