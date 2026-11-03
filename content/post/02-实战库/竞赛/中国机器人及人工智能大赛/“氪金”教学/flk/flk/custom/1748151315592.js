Blockly.Blocks['1748151315592'] = {
  init: function() {
    this.jsonInit({
      "type": "1748151315592",
      "message0": "下高台_1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1748151315592'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(107,168,10,98,92,55,123,99,97,20,190,100,107,143,76,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(107,168,10,107,94,23,153,115,96,19,190,111,98,159,57,138,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(107,168,10,107,94,23,153,115,97,20,190,107,83,52,139,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(107,168,10,106,138,60,134,109,97,20,190,107,136,110,128,103,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(107,168,10,107,160,150,83,114,97,20,190,108,111,111,38,95,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(107,168,10,110,160,150,39,101,97,20,190,110,115,184,91,105,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(107,168,10,108,103,150,39,100,97,20,190,110,115,184,91,105,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(107,168,10,98,92,55,123,99,97,20,190,100,107,143,76,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(107,168,10,100,90,59,70,99,97,20,190,100,107,136,134,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(107,168,10,100,133,150,36,101,97,20,190,101,63,50,165,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(107,168,10,82,158,150,70,83,97,20,190,130,43,57,116,128,128,71,100)\nMOTOwait()\nMOTOsetspeed(23)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1748151315592'] = function(block) {
  let code = "robot.leju_action('下高台_1')\n";
  return code;
}

