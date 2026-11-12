Blockly.Blocks['1752839487126'] = {
  init: function() {
    this.jsonInit({
      "type": "1752839487126",
      "message0": "1共",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752839487126'] = function(block) {
  let code = "MOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65)\nMOTOsetspeed(50)\nMOTOmove19(64,10,180,100,93,55,124,100,137,190,23,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(64,10,180,90,91,47,133,86,137,190,23,94,107,146,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64,10,180,86,125,95,110,90,137,190,23,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,180,86,113,37,156,88,137,190,23,94,107,146,77,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64,10,180,107,100,56,124,111,137,190,23,112,129,155,93,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,180,107,100,56,124,111,137,190,23,112,99,131,90,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,180,107,100,56,124,111,137,190,23,112,66,112,69,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64,10,180,109,95,63,117,100,137,190,23,112,97,114,95,102,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,180,100,93,55,124,100,137,190,23,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752839487126'] = function(block) {
  let code = "robot.leju_action('1共')\n";
  return code;
}

