Blockly.Blocks['1748150158421'] = {
  init: function() {
    this.jsonInit({
      "type": "1748150158421",
      "message0": "as",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1748150158421'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,30,20,20,65,75,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,92,66,56,89,95,130,176,10,105,76,159,37,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(66,26,190,92,80,67,94,91,130,176,10,109,83,162,39,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,100,93,55,124,100,130,176,10,100,107,145,76,100,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(20)\nMOTOmove19(66,26,190,101,66,63,91,99,130,176,10,104,81,143,49,102,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,26,190,100,93,55,124,100,130,176,10,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1748150158421'] = function(block) {
  let code = "robot.leju_action('as')\n";
  return code;
}

