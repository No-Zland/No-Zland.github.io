Blockly.Blocks['1748149671675'] = {
  init: function() {
    this.jsonInit({
      "type": "1748149671675",
      "message0": "2块右转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1748149671675'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,87,114,34,172,90,130,176,10,108,149,157,104,108,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,100,93,55,124,100,130,176,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1748149671675'] = function(block) {
  let code = "robot.leju_action('2块右转')\n";
  return code;
}

