Blockly.Blocks['1747910119127'] = {
  init: function() {
    this.jsonInit({
      "type": "1747910119127",
      "message0": "box_go_min3",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1747910119127'] = function(block) {
  let code = "MOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65)\nMOTOsetspeed(50)\nMOTOmove19(66,21,190,100,93,55,124,100,129,174,10,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(66,21,190,90,91,47,133,86,129,174,10,94,107,146,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(66,21,190,86,125,95,110,90,129,174,10,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,86,113,37,156,88,129,174,10,94,107,146,77,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(66,21,190,107,100,56,124,111,129,174,10,112,129,155,93,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(66,21,190,106,95,54,123,113,129,174,10,114,75,105,90,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(66,21,190,106,93,54,123,111,129,174,10,114,87,163,44,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(66,21,190,88,71,45,107,90,129,174,10,93,100,144,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(66,21,190,86,125,95,110,90,129,174,10,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(8)\nMOTOmove19(66,21,190,100,93,55,124,100,129,174,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1747910119127'] = function(block) {
  let code = "robot.leju_action('box_go_min3')\n";
  return code;
}

