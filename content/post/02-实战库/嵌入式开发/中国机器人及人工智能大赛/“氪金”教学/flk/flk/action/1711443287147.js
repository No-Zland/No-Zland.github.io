Blockly.Blocks['1711443287147'] = {
  init: function() {
    this.jsonInit({
      "type": "1711443287147",
      "message0": "box_go2_dg",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711443287147'] = function(block) {
  let code = "MOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65)\nMOTOsetspeed(50)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64,10,164,90,91,48,129,88,137,190,37,94,107,146,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64,10,164,86,125,95,110,90,137,190,37,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64,10,164,86,113,37,156,88,137,190,37,94,107,146,77,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64,10,164,107,100,56,124,111,137,190,37,112,129,155,93,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64,10,164,106,95,54,123,113,137,190,37,114,75,105,90,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64,10,164,106,93,54,123,111,137,190,37,114,87,163,44,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64,10,164,88,71,45,107,90,137,190,37,93,100,144,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64,10,164,86,125,95,110,90,137,190,37,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711443287147'] = function(block) {
  let code = "robot.leju_action('box_go2_dg')\n";
  return code;
}

