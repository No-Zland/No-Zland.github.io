Blockly.Blocks['1749030527097'] = {
  init: function() {
    this.jsonInit({
      "type": "1749030527097",
      "message0": "抱块_1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1749030527097'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,95,95,150,45,97,155,178,35,97,100,50,153,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(42,39,172,60,110,150,46,64,154,177,35,136,90,50,154,138,128,71,98)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,39,155,48,130,150,46,64,154,176,45,144,68,50,154,138,128,71,98)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(41,91,166,48,130,150,46,64,154,113,40,144,68,50,154,138,128,71,98)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(42,52,150,99,110,43,142,92,141,171,48,111,88,158,56,108,128,71,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1749030527097'] = function(block) {
  let code = "robot.leju_action('抱块_1')\n";
  return code;
}

