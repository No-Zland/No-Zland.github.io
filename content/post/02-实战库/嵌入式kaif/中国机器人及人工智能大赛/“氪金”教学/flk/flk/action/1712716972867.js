Blockly.Blocks['1712716972867'] = {
  init: function() {
    this.jsonInit({
      "type": "1712716972867",
      "message0": "高台box-go",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1712716972867'] = function(block) {
  let code = "MOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65)\nMOTOsetspeed(50)\nMOTOmove19(75,10,169,100,93,55,124,100,122,190,31,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(75,10,169,90,91,48,129,88,122,190,31,94,107,146,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(75,10,169,86,125,95,110,90,122,190,31,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(75,10,169,86,113,37,156,88,122,190,31,94,107,146,77,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(75,10,169,107,100,56,124,111,122,190,31,112,129,155,93,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(75,10,169,106,95,54,123,113,122,190,31,114,75,105,90,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(75,10,169,106,93,54,123,111,122,190,31,114,87,163,44,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(75,10,169,88,71,45,107,90,122,190,31,93,100,144,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(75,10,169,86,125,95,110,90,122,190,31,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(75,10,169,86,113,37,156,88,122,190,31,94,107,146,77,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(75,10,169,100,93,55,124,100,122,190,31,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1712716972867'] = function(block) {
  let code = "robot.leju_action('高台box-go')\n";
  return code;
}

