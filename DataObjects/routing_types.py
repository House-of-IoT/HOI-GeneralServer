class RoutingTypes:
    GENERIC_STATE_WITH_NO_AUTH = {
        "contact_list",
        "recent_connections",
        "executed_actions",
        "task_list",
        "server_config",
        "recent_executed_tasks"}

    GENERIC_STATE_WITH_NO_AUTH_CAPTURE_MANAGER = {
        "contact_list",
        "recent_connections",
        "executed_actions"}

    STATE_OR_RECORD_MODIFICATION = {
        "add-task",
        "remove-task",
        "add-contact",
        "remove-contact"
    }

    BASIC_ACTIONS = {
        "test_trigger"
    }