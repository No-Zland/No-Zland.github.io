Blockly.Blocks['1752839225001'] = {
  init: function() {
    this.jsonInit({
      "type": "1752839225001",
      "message0": "1右转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752839225001'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,87,114,34,172,90,138,190,37,108,149,157,104,108,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,138,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752839225001'] = function(block) {
  let code = "robot.leju_action('1右转')\n";
  return code;
}

