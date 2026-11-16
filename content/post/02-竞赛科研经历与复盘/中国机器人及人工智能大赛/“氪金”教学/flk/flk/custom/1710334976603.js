Blockly.Blocks['1710334976603'] = {
  init: function() {
    this.jsonInit({
      "type": "1710334976603",
      "message0": "抱块前走pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710334976603'] = function(block) {
  let code = "MOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65)\nMOTOsetspeed(6)\nMOTOmove19(42,38,173,90,91,48,134,88,155,178,35,94,109,146,71,89,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,86,123,95,115,90,155,178,35,94,109,146,71,87,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,86,121,37,161,88,155,178,35,94,109,146,72,89,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(42,38,173,107,98,56,129,111,155,178,35,112,131,155,88,110,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,106,93,54,128,113,155,178,35,114,77,105,85,110,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,106,91,54,128,111,155,178,35,114,89,163,39,112,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(42,38,173,88,69,45,112,90,155,178,35,93,102,144,71,89,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,86,123,95,115,90,155,178,35,94,107,146,72,87,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,100,91,55,129,100,155,178,35,100,109,145,71,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710334976603'] = function(block) {
  let code = "robot.leju_action('抱块前走pro')\n";
  return code;
}

