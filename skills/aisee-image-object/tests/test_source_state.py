from __future__ import annotations

from source_state import add_operation, empty_state, next_id, save_state, load_state


def test_next_id_and_operation_are_stable(tmp_path):
    state = empty_state(tmp_path)
    assert state["regions"] == []
    assert next_id(state, "masks", "mask") == "mask_001"
    state["masks"].append({"id": "mask_001"})
    assert next_id(state, "masks", "mask") == "mask_002"

    op = add_operation(state, "refine-mask", outputs=["masks/mask_002.png"])
    assert op["id"] == "op_001"
    assert op["status"] == "success"

    save_state(tmp_path, state)
    loaded = load_state(tmp_path)
    assert loaded["regions"] == []
    assert loaded["operations"][0]["kind"] == "refine-mask"
