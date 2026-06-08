-- Ageu Assunção Simões Galindo - O Bulovask Louco
drop database if exists companhiaaerea;
create database companhiaaerea;
use companhiaaerea;


create table Cliente (
    id_cliente int auto_increment primary key,
    nome varchar(100) not null,
    email varchar(100) unique not null,
    telefone varchar(20),
    documento_fiscal varchar(20) unique not null
);

create table Passageiro (
    id_passageiro int auto_increment primary key,
    nome_completo varchar(100) not null,
    documento_identidade varchar(20) unique not null,
    data_nascimento date not null
);

create table Voo (
    id_voo int auto_increment primary key,
    numero_voo varchar(10) not null,
    origem char(3) not null,
    destino char(3) not null,
    partida_prevista datetime not null,
    chegada_prevista datetime not null,
    aeronave_modelo varchar(50)
);

create table Reserva (
    id_reserva int auto_increment primary key,
    id_cliente int not null,
    codigo_reserva varchar(10) unique not null,
    data_reserva timestamp default CURRENT_TIMESTAMP,
    status_pagamento enum('Pendente', 'Confirmado', 'Cancelado') default 'Pendente',
    foreign key (id_cliente) references Cliente(id_cliente)
);

create table Bilhete (
    id_bilhete int auto_increment primary key,
    id_reserva int not null,
    id_voo int not null,
    id_passageiro int not null,
    numero_bilhete varchar(20) unique not null,
    assento_atribuido varchar(5),
    classe enum('Economica', 'Executiva', 'Primeira Classe') not null,
    preco_pago decimal(10, 2) not null,
    foreign key (id_reserva) references Reserva(id_reserva) on delete cascade,
    foreign key (id_voo) references Voo(id_voo),
    foreign key (id_passageiro) references Passageiro(id_passageiro)
);



