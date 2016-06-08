from omero_basics import OMEROConnectionManager
import utils

form_schemas = [
    (
        'simple',
        """
{
  "title": "A registration form",
  "type": "object",
  "required": [
    "firstName",
    "lastName"
  ],
  "properties": {
    "firstName": {
      "type": "string",
      "title": "First name"
    },
    "lastName": {
      "type": "string",
      "title": "Last name"
    },
    "age": {
      "type": "integer",
      "title": "Age"
    },
    "bio": {
      "type": "string",
      "title": "Bio"
    },
    "password": {
      "type": "string",
      "title": "Password",
      "minLength": 3
    }
  }
}
        """,
        """
{
  "age": {
    "ui:widget": "updown"
  },
  "bio": {
    "ui:widget": "textarea"
  },
  "password": {
    "ui:widget": "password",
    "ui:help": "Hint: Make it strong!"
  },
  "date": {
    "ui:widget": "alt-datetime"
  }
}
        """
    ),
    (
        'nested',
        """
{
  "title": "A list of tasks",
  "type": "object",
  "required": [
    "title"
  ],
  "properties": {
    "title": {
      "type": "string",
      "title": "Task list title"
    },
    "tasks": {
      "type": "array",
      "title": "Tasks",
      "items": {
        "type": "object",
        "required": [
          "title"
        ],
        "properties": {
          "title": {
            "type": "string",
            "title": "Title",
            "description": "A sample title"
          },
          "details": {
            "type": "string",
            "title": "Task details",
            "description": "Enter the task details"
          },
          "done": {
            "type": "boolean",
            "title": "Done?",
            "default": false
          }
        }
      }
    }
  }
}
        """,
        """
{
  "tasks": {
    "items": {
      "details": {
        "ui:widget": "textarea"
      }
    }
  }
}
        """
    ),
    (
        'arrays',
        """
{
  "type": "object",
  "properties": {
    "listOfStrings": {
      "type": "array",
      "title": "A list of strings",
      "items": {
        "type": "string",
        "default": "bazinga"
      }
    },
    "multipleChoicesList": {
      "type": "array",
      "title": "A multiple choices list",
      "items": {
        "type": "string",
        "enum": [
          "foo",
          "bar",
          "fuzz",
          "qux"
        ]
      },
      "uniqueItems": true
    },
    "fixedItemsList": {
      "type": "array",
      "title": "A list of fixed items",
      "items": [
        {
          "title": "A string value",
          "type": "string",
          "default": "lorem ipsum"
        },
        {
          "title": "a boolean value",
          "type": "boolean"
        }
      ],
      "additionalItems": {
        "title": "Additional item",
        "type": "number"
      }
    },
    "nestedList": {
      "type": "array",
      "title": "Nested list",
      "items": {
        "type": "array",
        "title": "Inner list",
        "items": {
          "type": "string",
          "default": "lorem ipsum"
        }
      }
    }
  }
}
        """,
        """
{
  "multipleChoicesList": {
    "ui:widget": "checkboxes"
  },
  "fixedItemsList": {
    "items": [
      {
        "ui:widget": "textarea"
      },
      {
        "ui:widget": "select"
      }
    ],
    "additionalItems": {
      "ui:widget": "updown"
    }
  }
}
        """
    ),
    (
        'numbers',
        """
{
  "type": "object",
  "title": "Number fields & widgets",
  "properties": {
    "number": {
      "title": "Number",
      "type": "number"
    },
    "integer": {
      "title": "Integer",
      "type": "integer"
    },
    "numberEnum": {
      "type": "number",
      "title": "Number enum",
      "enum": [
        1,
        2,
        3
      ]
    },
    "integerRange": {
      "title": "Integer range",
      "type": "integer",
      "minimum": 42,
      "maximum": 100
    },
    "integerRangeSteps": {
      "title": "Integer range (by 10)",
      "type": "integer",
      "minimum": 50,
      "maximum": 100,
      "multipleOf": 10
    }
  }
}
        """,
        """
{
  "integer": {
    "ui:widget": "updown"
  },
  "integerRange": {
    "ui:widget": "range"
  },
  "integerRangeSteps": {
    "ui:widget": "range"
  }
}
        """
    ),
    (
        'widgets',
        """
{
  "title": "Widgets",
  "type": "object",
  "properties": {
    "stringFormats": {
      "type": "object",
      "title": "String formats",
      "properties": {
        "email": {
          "type": "string",
          "format": "email"
        },
        "uri": {
          "type": "string",
          "format": "uri"
        }
      }
    },
    "boolean": {
      "type": "object",
      "title": "Boolean field",
      "properties": {
        "default": {
          "type": "boolean",
          "title": "checkbox (default)"
        },
        "radio": {
          "type": "boolean",
          "title": "radio buttons"
        },
        "select": {
          "type": "boolean",
          "title": "select box"
        }
      }
    },
    "string": {
      "type": "object",
      "title": "String field",
      "properties": {
        "default": {
          "type": "string",
          "title": "text input (default)"
        },
        "textarea": {
          "type": "string",
          "title": "textarea"
        },
        "color": {
          "type": "string",
          "title": "color picker",
          "default": "#151ce6"
        }
      }
    },
    "secret": {
      "type": "string",
      "default": "I'm a hidden string."
    },
    "disabled": {
      "type": "string",
      "title": "A disabled field",
      "default": "I am disabled."
    },
    "readonly": {
      "type": "string",
      "title": "A readonly field",
      "default": "I am read-only."
    }
  }
}
        """,
        """
{
  "boolean": {
    "radio": {
      "ui:widget": "radio"
    },
    "select": {
      "ui:widget": "select"
    }
  },
  "string": {
    "textarea": {
      "ui:widget": "textarea"
    },
    "color": {
      "ui:widget": "color"
    }
  },
  "secret": {
    "ui:widget": "hidden"
  },
  "disabled": {
    "ui:disabled": true
  },
  "readonly": {
    "ui:readonly": true
  }
}
        """
    ),
    (
        'ordering',
        """
{
  "title": "An ordered registration form",
  "type": "object",
  "required": [
    "firstName",
    "lastName"
  ],
  "properties": {
    "password": {
      "type": "string",
      "title": "Password"
    },
    "lastName": {
      "type": "string",
      "title": "Last name"
    },
    "bio": {
      "type": "string",
      "title": "Bio"
    },
    "firstName": {
      "type": "string",
      "title": "First name"
    },
    "age": {
      "type": "integer",
      "title": "Age"
    }
  }
}
        """,
        """
{
  "ui:order": [
    "firstName",
    "lastName",
    "age",
    "bio",
    "password"
  ],
  "age": {
    "ui:widget": "updown"
  },
  "bio": {
    "ui:widget": "textarea"
  },
  "password": {
    "ui:widget": "password"
  }
}
        """
    ),
    (
        'references',
        """
{
  "definitions": {
    "address": {
      "type": "object",
      "properties": {
        "street_address": {
          "type": "string"
        },
        "city": {
          "type": "string"
        },
        "state": {
          "type": "string"
        }
      },
      "required": [
        "street_address",
        "city",
        "state"
      ]
    }
  },
  "type": "object",
  "properties": {
    "billing_address": {
      "title": "Billing address",
      "$ref": "#/definitions/address"
    },
    "shipping_address": {
      "title": "Shipping address",
      "$ref": "#/definitions/address"
    }
  }
}
        """,
        """
{
  "ui:order": [
    "shipping_address",
    "billing_address"
  ]
}
        """
    ),
    (
        'custom',
        """
{
  "title": "A localisation form",
  "type": "object",
  "required": [
    "lat",
    "lon"
  ],
  "properties": {
    "lat": {
      "type": "number"
    },
    "lon": {
      "type": "number"
    }
  }
}
        """,
        """
{
  "ui:field": "geo"
}
        """
    ),
    (
        'errors',
        """
{
  "title": "Contextualized errors",
  "type": "object",
  "properties": {
    "firstName": {
      "type": "string",
      "title": "First name",
      "minLength": 8,
      "pattern": "\\\d+"
    },
    "active": {
      "type": "boolean",
      "title": "Active"
    },
    "skills": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 5
      }
    },
    "multipleChoicesList": {
      "type": "array",
      "title": "Pick max two items",
      "uniqueItems": true,
      "maxItems": 2,
      "items": {
        "type": "string",
        "enum": [
          "foo",
          "bar",
          "fuzz"
        ]
      }
    }
  }
}
        """,
        """
{}
        """
    ),
    (
        'large',
        """
{
  "definitions": {
    "largeEnum": {
      "type": "string",
      "enum": [
        "option #0",
        "option #1",
        "option #2",
        "option #3",
        "option #4",
        "option #5",
        "option #6",
        "option #7",
        "option #8",
        "option #9",
        "option #10",
        "option #11",
        "option #12",
        "option #13",
        "option #14",
        "option #15",
        "option #16",
        "option #17",
        "option #18",
        "option #19",
        "option #20",
        "option #21",
        "option #22",
        "option #23",
        "option #24",
        "option #25",
        "option #26",
        "option #27",
        "option #28",
        "option #29",
        "option #30",
        "option #31",
        "option #32",
        "option #33",
        "option #34",
        "option #35",
        "option #36",
        "option #37",
        "option #38",
        "option #39",
        "option #40",
        "option #41",
        "option #42",
        "option #43",
        "option #44",
        "option #45",
        "option #46",
        "option #47",
        "option #48",
        "option #49",
        "option #50",
        "option #51",
        "option #52",
        "option #53",
        "option #54",
        "option #55",
        "option #56",
        "option #57",
        "option #58",
        "option #59",
        "option #60",
        "option #61",
        "option #62",
        "option #63",
        "option #64",
        "option #65",
        "option #66",
        "option #67",
        "option #68",
        "option #69",
        "option #70",
        "option #71",
        "option #72",
        "option #73",
        "option #74",
        "option #75",
        "option #76",
        "option #77",
        "option #78",
        "option #79",
        "option #80",
        "option #81",
        "option #82",
        "option #83",
        "option #84",
        "option #85",
        "option #86",
        "option #87",
        "option #88",
        "option #89",
        "option #90",
        "option #91",
        "option #92",
        "option #93",
        "option #94",
        "option #95",
        "option #96",
        "option #97",
        "option #98",
        "option #99"
      ]
    }
  },
  "title": "A rather large form",
  "type": "object",
  "properties": {
    "string": {
      "type": "string",
      "title": "Some string"
    },
    "choice1": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice2": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice3": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice4": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice5": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice6": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice7": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice8": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice9": {
      "$ref": "#/definitions/largeEnum"
    },
    "choice10": {
      "$ref": "#/definitions/largeEnum"
    }
  }
}
        """,
        """
{}
        """
    ),
    (
        'datetime',
        """
{
  "title": "Date and time widgets",
  "type": "object",
  "properties": {
    "native": {
      "title": "Native",
      "description": "May not work on some browsers, notably Firefox Desktop and IE.",
      "type": "object",
      "properties": {
        "datetime": {
          "type": "string",
          "format": "date-time"
        },
        "date": {
          "type": "string",
          "format": "date"
        }
      }
    },
    "alternative": {
      "title": "Alternative",
      "description": "These work on every platform.",
      "type": "object",
      "properties": {
        "alt-datetime": {
          "type": "string",
          "format": "date-time"
        },
        "alt-date": {
          "type": "string",
          "format": "date"
        }
      }
    }
  }
}
        """,
        """
{
  "alternative": {
    "alt-datetime": {
      "ui:widget": "alt-datetime"
    },
    "alt-date": {
      "ui:widget": "alt-date"
    }
  }
}
        """
    ),
    (
        'validation',
        """
{
  "title": "Custom validation",
  "description": "This form defines custom validation rules checking that the two passwords match.",
  "type": "object",
  "properties": {
    "pass1": {
      "title": "Password",
      "type": "string",
      "minLength": 3
    },
    "pass2": {
      "title": "Repeat password",
      "type": "string",
      "minLength": 3
    }
  }
}
        """,
        """
{
  "pass1": {
    "ui:widget": "password"
  },
  "pass2": {
    "ui:widget": "password"
  }
}
        """
    ),
    (
        'files',
        """
{
  "title": "Files",
  "type": "object",
  "properties": {
    "file": {
      "type": "string",
      "format": "data-url",
      "title": "Single file"
    },
    "files": {
      "type": "array",
      "title": "Multiple files",
      "items": {
        "type": "string",
        "format": "data-url"
      }
    }
  }
}
        """,
        """
{}
        """
    )

]

su_conn_manager = OMEROConnectionManager(config_file="omero_su.cfg")
su_conn = su_conn_manager.connect()

conn_manager = OMEROConnectionManager(config_file="omero.cfg")
conn = conn_manager.connect()

master_user_id = 252L
group_ids = [203L]

for form in utils.list_forms(su_conn, master_user_id):
    utils.delete_form(su_conn, master_user_id, form['form_id'])
    utils.delete_form_data(su_conn, master_user_id, form['form_id'], 'Dataset',
                           251L)
    utils.delete_form_kvdata(conn, form['form_id'], 'Dataset', 251L)

# for form_schema in form_schemas:
#     form_id, form_json, form_ui = form_schema
#     # print form_id, form_json, form_ui
#     utils.add_form(su_conn, master_user_id, form_id, form_json, form_ui,
#                    group_ids)
