Blockly.Blocks['1752839291360'] = {
  init: function() {
    this.jsonInit({
      "type": "1752839291360",
      "message0": "1左转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752839291360'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,95,49,50,87,96,138,190,37,97,88,181,20,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,138,190,37,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752839291360'] = function(block) {
  let code = "robot.leju_action('1左转')\n";
  return code;
}

