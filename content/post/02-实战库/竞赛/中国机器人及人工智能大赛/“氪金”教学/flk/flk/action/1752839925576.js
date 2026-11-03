Blockly.Blocks['1752839925576'] = {
  init: function() {
    this.jsonInit({
      "type": "1752839925576",
      "message0": "1fang",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752839925576'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\n\n\n-- 1\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,130,98,138,190,37,100,107,145,70,102,120,40,100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(20)\nMOTOmove19(64,10,164,100,93,55,124,100,138,190,37,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64,10,164,99,101,150,38,97,138,190,37,100,97,50,164,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64,10,164,95,127,150,39,95,138,190,37,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,62,141,95,127,150,39,95,121,145,56,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(74,58,141,97,113,120,76,99,118,143,58,99,86,79,123,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752839925576'] = function(block) {
  let code = "robot.leju_action('1fang')\n";
  return code;
}

