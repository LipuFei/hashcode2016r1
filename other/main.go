package main

import (
	"io/ioutil"
	"fmt"
	"encoding/json"
)

// types
type Item struct {
	id     uint
	weight uint
}
type warehouseJson struct {
	Location []uint `json:"location"`
	Items    []uint `json:"item_count_list"`
}
type Warehouse struct {
	Id    int
	X     uint
	Y     uint
	Items []uint
}
type Drone struct {
	id    uint
	state uint
	x     uint
	y     uint
}

type Order struct {
	id    uint
	x     uint
	y     uint
	items []Item
}

// data?
var Warehouses []Warehouse

func main() {
	getWarehouses()
}

func getWarehouses() {
	data, err := ioutil.ReadFile("json/busyday_warehouse.json")
	if err != nil {
		fmt.Println(err)
	}

	var myjson []warehouseJson
	err = json.Unmarshal(data, &myjson)
	if err != nil {
		fmt.Println(err)
	}
	//fmt.Printf("%#v", myjson)
	for i, j := range myjson {
		Warehouses = append(Warehouses, Warehouse{
			Id: i,
			X: j.Location[0],
			Y: j.Location[1],
			Items: j.Items,
		})
	}
}